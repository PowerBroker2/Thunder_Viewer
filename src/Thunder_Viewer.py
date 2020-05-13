import os
import sys
import json
import shutil
import struct
import requests
import datetime as dt
import paho.mqtt.client as mqtt
from random import randint
from getpass import getuser
from socketserver import TCPServer, BaseRequestHandler
from PyQt5.QtCore import QThread, QProcess, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
from pySerialTransfer import pySerialTransfer as transfer
from WarThunder import general, telemetry, acmi, mapinfo
from WarThunder.telemetry import combine_dicts
from remotePlayGui import Ui_PlayerManager
from usbFieldsGui import Ui_usbFieldManager
from gui import Ui_ThunderViewer


USERNAME     = getuser()
BROKER_HOST  = 'broker.hivemq.com'
TIME_FORMAT  = '%Y-%m-%dT%H:%M:%S.%f'
APP_DIR      = os.path.dirname(os.path.realpath(__file__))
LOGS_DIR     = os.path.join(APP_DIR, 'logs')
MQTT_DIR     = os.path.join(APP_DIR, 'mqtt')
REMOTE_DIR   = os.path.join(MQTT_DIR, 'remote_players')
REF_FILE     = os.path.join(MQTT_DIR, 'reference.txt')
TEXTURES_DIR = os.path.join(os.environ['APPDATA'], r'Tacview\Data\Terrain\Textures')
XML_NAME     = 'CustomTextureList.xml'
TEXTURE_XML_TEMPLATE  = os.path.join(APP_DIR, XML_NAME)
TEXTURE_XML  = os.path.join(TEXTURES_DIR, XML_NAME)
TITLE_FORMAT = '{timestamp}_{user}.acmi'
ACMI_HEADER  = {'DataSource': '',
                'DataRecorder': '',
                'Author': '',
                'Title': '',
                'Comments': '',
                'ReferenceLongitude': 0,
                'ReferenceLatitude': 0}
ACMI_ENTRY   = {'T': '',
                'Throttle': 0,
                'RollControlInput': 0,
                'PitchControlInput': 0,
                'YawControlInput': 0,
                'IAS': 0,
                'TAS': 0,
                'FuelWeight': 0,
                'FuelVolume': 0,
                'Mach': 0,
                'AOA': 0,
                'LandingGear': 0,
                'Flaps': 0}
INITIAL_META = {'Slot': 0,
                'Importance': 1,
                'Parachute': 0,
                'DragChute': 0,
                'Disabled': 0,
                'Pilot': 0,
                'Name': '',
                'Type': '',
                'Color': None,
                'Callsign': None,
                'Coalition': None}
glob_ref_time = False


def format_header_dict(grid_info, loc_time):
    '''
    Description:
    ------------
    Create a dictionary of formatted telemetry samples to be logged in the
    ACMI log
    
    :param grid_info: dict     - map location metadata
    :param loc_time:  datetime - local date/time at the time of ACMI log creation
    
    :return formatted_header: dict - all additional fields and values desired
                                     in the ACMI log header
    '''
    
    formatted_header = ACMI_HEADER
    
    formatted_header['DataSource']         = 'War Thunder v{}'.format(general.get_version())
    formatted_header['DataRecorder']       = 'Thunder Viewer'
    formatted_header['Author']             = getuser()
    formatted_header['Title']              = grid_info['name']
    formatted_header['Comments']           = 'Local: {}'.format(loc_time.strftime('%Y-%m-%d %H:%M:%S'))
    formatted_header['ReferenceLatitude']  = grid_info['ULHC_lat']
    formatted_header['ReferenceLongitude'] = grid_info['ULHC_lon']
    
    return formatted_header

def format_entry_dict(telem, team_flag=True, initial_entry=False):
    '''
    Description:
    ------------
    Create a dictionary of formatted telemetry samples to be logged in the
    ACMI log
    
    :param telem: dict - full War Thunder vehicle telemetry data
    
    :return formatted_entry: dict - all fields and values necessary for a new
                                    entry in the ACMI log
    '''
    
    formatted_entry = ACMI_ENTRY
    
    formatted_entry['T'] = ('{lon:0.9f}|'
                            '{lat:0.9f}|'
                            '{alt}|'
                            '{roll:0.1f}|'
                            '{pitch:0.1f}|'
                            '{hdg:0.1f}').format(lon=telem['lon'],
                                                 lat=telem['lat'],
                                                 alt=telem['alt_m'],
                                                 roll=telem['aviahorizon_roll'],
                                                 pitch=telem['aviahorizon_pitch'],
                                                 hdg=telem['compass'])
                              
    formatted_entry['Throttle']          = telem['throttle 1, %'] / 100
    formatted_entry['RollControlInput']  = '{0:.6f}'.format(telem['stick_ailerons'])
    formatted_entry['PitchControlInput'] = '{0:.6f}'.format(telem['stick_elevator'])
    
    try:
        formatted_entry['YawControlInput'] = '{0:.6f}'.format(telem['pedals1'])
    except KeyError:
        formatted_entry['YawControlInput'] = 0
        
    formatted_entry['IAS']               = '{0:.6f}'.format(telem['IAS, km/h'])
    formatted_entry['TAS']               = telem['TAS, km/h']
    formatted_entry['FuelWeight']        = telem['Mfuel, kg']
    formatted_entry['FuelVolume']        = telem['Mfuel, kg'] / telem['Mfuel0, kg']
    formatted_entry['Mach']              = telem['M']
    
    try:
        formatted_entry['AOA'] = telem['AoA, deg']
    except KeyError:
        formatted_entry['AOA'] = 0
    
    try:
        formatted_entry['LandingGear'] = telem['gear, %'] / 100
    except KeyError:
        formatted_entry['LandingGear'] = 1
    
    try:
        formatted_entry['Flaps'] = telem['flaps, %'] / 100
    except KeyError:
        formatted_entry['Flaps'] = 0
    
    if initial_entry:
        formatted_entry = combine_dicts(formatted_entry,
                                        format_init_meta(telem, team_flag))
    
    return formatted_entry

def format_init_meta(telem, team_flag=True):
    '''
    Description:
    ------------
    Create a dictionary of formatted object metadata to be logged in the
    ACMI log (only needed once per object to be displayed)
    
    :param telem: dict - full War Thunder vehicle telemetry data
    
    :return formatted_meta: dict - all object metadata fields and values 
                                   necessary for it's initial entry in the ACMI log
    '''
    
    formatted_meta = INITIAL_META
    
    formatted_meta['Name'] = telem['type']
    formatted_meta['Type'] = 'Air+FixedWing'
    
    if team_flag:
        formatted_meta['Coalition'] = 'Blue_Team'
        formatted_meta['Color']     = 'Blue'
    else:
        formatted_meta['Coalition'] = 'Red_Team'
        formatted_meta['Color']     = 'Red'
    
    return formatted_meta

def gen_id():
    '''
    Description:
    ------------
    Find a valid Tacview object hex ID
    
    :return: str - new object hex ID
    '''
    
    return str(hex(randint(1, acmi.MAX_NUM_OBJS + 2))[2:]).upper()


class PlayerManager(QMainWindow):
    def __init__(self, parent=None):
        super(PlayerManager, self).__init__(parent)


class AppWindow(QMainWindow):
    '''
    Description:
    ------------
    Main GUI window class
    '''
    
    def __init__(self):
        super().__init__()
        self.ui = Ui_ThunderViewer()
        self.ui.setupUi(self)
        self.show()
        
        self.PlayerManager = QMainWindow()
        self.PlayerManager_ui = Ui_PlayerManager()
        self.PlayerManager_ui.setupUi(self.PlayerManager)
        
        self.UsbManager = QMainWindow()
        self.UsbManager_ui = Ui_usbFieldManager()
        self.UsbManager_ui.setupUi(self.UsbManager)
        
        self.connect_signals()
        self.init_recording_status()
        self.update_port_list()
        
        self.ui.acmi_path.setText(LOGS_DIR)
        self.enable_inputs()
        self.find_tacview_install()
        
        self.player_names = []
    
    def connect_signals(self):
        '''
        Description:
        ------------
        Connect button clicks to callback functions
        '''
        
        self.ui.tacview_select.clicked.connect(self.get_tacview_install)
        self.ui.acmi_select.clicked.connect(self.get_acmi_dir)
        self.ui.launch_tacview_live.clicked.connect(self.launch_live)
        self.ui.record.clicked.connect(self.record_data)
        self.ui.stop.clicked.connect(self.stop_recording_data)
        self.ui.manage_players.clicked.connect(self.launch_remote_player_window)
        self.PlayerManager_ui.apply.clicked.connect(self.block_players)
        self.ui.manage_usb_fields.clicked.connect(self.launch_usb_fields_window)
        self.UsbManager_ui.apply.clicked.connect(self.update_usb_fields)
        self.ui.port_refresh.clicked.connect(self.update_port_list)
        
    def find_tacview_install(self):
        '''
        Description:
        ------------
        TODO
        '''
        
        x86_folder  = r'C:\Program Files (x86)'
        indep_install_folder = os.path.join(x86_folder, 'Tacview')
        steam_install_folder = os.path.join(x86_folder, 'Steam', 'steamapps', 'common', 'Tacview')
        appName = 'Tacview64.exe'
        app_found = False
        
        if os.path.exists(indep_install_folder):
            if appName in os.listdir(indep_install_folder):
                app_found = True
                self.ui.tacview_path.setText(os.path.join(indep_install_folder, appName))
        
        if os.path.exists(steam_install_folder) and not app_found:
            if appName in os.listdir(steam_install_folder):
                app_found = True
                self.ui.tacview_path.setText(os.path.join(steam_install_folder, appName))
        
        if not app_found:
            for dirName, subdirList, fileList in os.walk(x86_folder):
                if appName in fileList: 
                    self.ui.tacview_path.setText(os.path.join(dirName, appName))
    
    def get_tacview_install(self):
        path = QFileDialog.getOpenFileName(self, filter='Tacview (Tacview.exe Tacview64.exe)')[0]
        if path:
            self.ui.tacview_path.setText(path)
    
    def get_acmi_dir(self):
        path = QFileDialog.getExistingDirectory(self, 'Select Directory', APP_DIR)
        if path:
            self.ui.acmi_path.setText(path)
    
    def launch_live(self):
        '''
        Description:
        ------------
        Launch the application "Tacview" at the path as specified in the GUI
        '''
        
        try:
            if not os.path.exists(self.ui.tacview_path.text()):
                raise FileNotFoundError
            self.process = QProcess()
            self.process.startDetached('"{}" {}'.format(self.ui.tacview_path.text(), '/ConnectRealTimeTelemetry'))
        except (FileNotFoundError, OSError):
            print('ERROR: Tacview.exe not found')
        
    def record_data(self):
        '''
        Description:
        ------------
        Begin recording and streaming (if any streaming options are enabled)
        '''
        
        if not self.ui.recording.isChecked():
            self.disable_inputs()
            
            if self.ui.live_usb.isChecked():
                self.usb_port = self.ui.usb_ports.currentText()
                self.usb_baud = int(self.ui.usb_baud.currentText())
                self.transfer = transfer.SerialTransfer(self.usb_port, self.usb_baud)
            
            if self.ui.mqtt.isChecked():
                self.mqtt_sub_th = MqttSubThread(self)
                self.mqtt_sub_th.start()
                self.mqtt_sub_th.update_names.connect(self.update_player_names)
                self.mqtt_sub_th.send_data.connect(self.send_to_stream)
            
            if self.ui.live_telem.isChecked():
                self.stream_th = StreamThread(self)
                self.stream_th.start()
            
            self.rec_th = RecordThread(self)
            self.rec_th.start()
            self.rec_th.send_data.connect(self.send_to_stream)
            
            self.ui.recording.setChecked(True)
    
    def stop_recording_data(self):
        '''
        Description:
        ------------
        Stops recording and streaming (if any streaming options are enabled)
        by closing all currently running threads
        '''
        
        self.enable_inputs()
        
        if self.ui.live_usb.isChecked():
            self.transfer.close()
        
        try:
            if self.rec_th.isRunning():
                self.rec_th.terminate()
        except AttributeError:
            pass
        
        try:
            if self.stream_th.isRunning():
                self.stream_th.terminate()
        except AttributeError:
            pass
        
        try:
            if self.mqtt_sub_th.isRunning():
                self.mqtt_sub_th.terminate()
        except AttributeError:
            pass
        
        self.ui.recording.setChecked(False)
    
    def init_recording_status(self):
        '''
        Description:
        ------------
        Control radio button to display the recording status
        '''
        
        self.ui.recording.setDisabled(True)
        self.ui.recording.setChecked(False)
    
    def update_port_list(self):
        '''
        Description:
        ------------
        Find the names of all currently available serial ports
        '''
        
        ports = transfer.open_ports()
        self.ui.usb_ports.clear()
        self.ui.usb_ports.addItems(ports)
    
    def launch_remote_player_window(self):
        '''
        Description:
        ------------
        TODO
        '''
        
        self.PlayerManager_ui.player_list.addItems(self.player_names)
        self.PlayerManager.show()
    
    def launch_usb_fields_window(self):
        '''
        Description:
        ------------
        TODO
        '''
        
        self.UsbManager.show()
    
    @pyqtSlot(list)
    def update_player_names(self, names):
        self.player_names = names
    
    @pyqtSlot(str)
    def send_to_stream(self, line):
        try:
            StreamHandler.remote_data_buff.append(line)
        except AttributeError:
            pass
    
    def block_players(self):
        '''
        Description:
        ------------
        TODO
        '''
        
        blocked = []
        
        try:
            num_players = self.PlayerManager_ui.player_list.count()
            player_list = self.PlayerManager_ui.player_list
            
            for i in range(num_players):
                if not player_list.item(i).isSelected():
                    blocked.append(player_list.item(i).text())
            
            self.mqtt_sub_th.blocked_players = blocked
        except AttributeError:
            pass
    
    def update_usb_fields(self):
        '''
        Description:
        ------------
        TODO
        '''
        
        try:
            self.rec_th.usb_fields = [item.text() for item in self.UsbManager_ui.usb_fields.selectedItems()]
        except AttributeError:
            pass
    
    def enable_inputs(self):
        self.change_inputs(True)
    
    def disable_inputs(self):
        self.change_inputs(False)
    
    def change_inputs(self, enable):
        '''
        Description:
        ------------
        Enables/disables GUI widgets
        '''
        
        self.ui.acmi_path.setEnabled(enable)
        self.ui.acmi_select.setEnabled(enable)
        self.ui.live_telem.setEnabled(enable)
        self.ui.live_telem_port.setEnabled(enable)
        self.ui.mqtt.setEnabled(enable)
        self.ui.mqtt_id.setEnabled(enable)
        self.ui.manage_players.setEnabled(enable)
        self.ui.usb_ports.setEnabled(enable)
        self.ui.live_usb.setEnabled(enable)
        self.ui.port_refresh.setEnabled(enable)
        self.ui.usb_baud.setEnabled(enable)
        self.ui.manage_usb_fields.setEnabled(enable)
        self.ui.team.setEnabled(enable)
        self.ui.sample_rate.setEnabled(enable)
        self.ui.record.setEnabled(enable)
        self.ui.stop.setEnabled(not enable)


class RecordThread(QThread):
    '''
    Description:
    ------------
    Thread class used to record and stream personal match data
    '''
    
    send_data = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super(RecordThread, self).__init__(parent)
        
        self.telem   = telemetry.TelemInterface() # class used to query War Thunder telemetry
        self.logger  = acmi.ACMI()                # class used to log match data
        self.log_dir = parent.ui.acmi_path.text()
        self.mqtt_enable   = parent.ui.mqtt.isChecked()
        self.stream_enable = parent.ui.live_telem.isChecked()
        self.usb_enable    = parent.ui.live_usb.isChecked()
        self.team          = not parent.ui.team.currentIndex()
        self.sample_period = 1.0 / parent.ui.sample_rate.value()
        self.usb_fields    = []
        
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
        
        if self.mqtt_enable:
            if not os.path.exists(REMOTE_DIR):
                os.makedirs(REMOTE_DIR)
            
            self.mqtt_id = parent.ui.mqtt_id.text()
            self.mqttc   = mqtt.Client()
            
            if self.mqttc.connect(BROKER_HOST):
                print('ERROR: Could not connect to MQTT broker {}'.format(BROKER_HOST))
                self.mqtt_enable = False
            
            if not self.mqtt_id:
                print('ERROR: No remote session ID provided')
                self.mqtt_enable = False
        
        if self.usb_enable:
            self.usb_port   = parent.usb_port
            
            if not self.usb_port:
                self.usb_enable = False
            else:
                self.transfer = parent.transfer
    
    def init_mqtt_struct(self):
        '''
        Description:
        ------------
        Initialize the file structure needed for propper MQTT processing
        '''
        
        if not os.path.exists(REMOTE_DIR):
            os.makedirs(REMOTE_DIR)
            
        with open(REF_FILE, 'w') as f:
            f.write(self.logger.reference_time.isoformat())
            f.write('\n')
            f.write(self.logger.obj_ids['0'])
    
    def stuff_float(self, val, start_pos):
        '''
        Description:
        ------------
        Insert a 32-bit floating point value into the (pySerialTransfer) TX
        buffer starting at the specified index
        
        :param val:       float - value to be inserted into TX buffer
        :param start_pos: int   - index of TX buffer where the first byte of
                                  the float is to be stored in
        
        :return start_pos: int - index of the last byte of the float in the TX
                                 buffer + 1
        '''
        
        val_bytes = struct.pack('f', val)
        
        self.transfer.txBuff[start_pos] = val_bytes[0]
        start_pos += 1
        self.transfer.txBuff[start_pos] = val_bytes[1]
        start_pos += 1
        self.transfer.txBuff[start_pos] = val_bytes[2]
        start_pos += 1
        self.transfer.txBuff[start_pos] = val_bytes[3]
        start_pos += 1
        
        return start_pos
    
    def stuff_int(self, val, start_pos):
        '''
        Description:
        ------------
        Insert a 16-bit integer value into the (pySerialTransfer) TX buffer
        starting at the specified index
        
        :param val:       int - value to be inserted into TX buffer
        :param start_pos: int - index of TX buffer where the first byte of
                                the int is to be stored in
        
        :return start_pos: int - index of the last byte of the int in the TX
                                 buffer + 1
        '''
        
        val_bytes = (val).to_bytes(2, byteorder='little')
        
        self.transfer.txBuff[start_pos] = val_bytes[0]
        start_pos += 1
        self.transfer.txBuff[start_pos] = val_bytes[1]
        start_pos += 1
        
        return start_pos
        
    
    def send_usb_telem(self):
        '''
        Description:
        ------------
        Send specified telemetry info to USB device via pySerialTransfer
        '''
        
        send_len = 0
        
        if 'Roll Angle' in self.usb_fields:
            send_len = self.stuff_float(self.telem.basic_telemetry['roll'],
                                        send_len)
        
        if 'Pitch Angle' in self.usb_fields:
            send_len = self.stuff_float(self.telem.basic_telemetry['pitch'],
                                        send_len)
        
        if 'Heading' in self.usb_fields:
            send_len = self.stuff_int(int(self.telem.basic_telemetry['heading']),
                                      send_len)
        
        if 'Altitude (meters)' in self.usb_fields:
            send_len = self.stuff_int(int(self.telem.basic_telemetry['altitude']),
                                      send_len)
        
        if 'Airspeed (km/h)' in self.usb_fields:
            send_len = self.stuff_int(int(self.telem.basic_telemetry['IAS']),
                                      send_len)
        
        if 'Latitude (dd)' in self.usb_fields:
            send_len = self.stuff_float(self.telem.basic_telemetry['lat'],
                                        send_len)
        
        if 'Longitude (dd)' in self.usb_fields:
            send_len = self.stuff_float(self.telem.basic_telemetry['lon'],
                                        send_len)
        
        if 'Flap State' in self.usb_fields:
            flap_state = int(self.telem.basic_telemetry['flapState'] / 100) # convert from % to bool
            
            self.transfer.txBuff[send_len] = flap_state
            send_len += 1
        
        if 'Gear State' in self.usb_fields:
            gear_state = int(self.telem.basic_telemetry['gearState'] / 100) # convert from % to bool
            
            self.transfer.txBuff[send_len] = gear_state
            send_len += 1
        
        self.transfer.send(send_len)
    
    def save_texture_files(self):
        '''
        Description:
        ------------
        Add current War Thunder match map to Tacview's custom terrain textures.
        This allows the map to be displayed on Tacview's Globe during replays
        and streams
        '''
        map_name = self.telem.map_info.grid_info['name']
        
        if not map_name == 'UNKNOWN':
            map_dim    = self.telem.map_info.grid_info['size_km']
            image_name = '{}.jpg'.format(map_name)
            
            ULHC_lon = self.telem.map_info.grid_info['ULHC_lon']
            ULHC_lat = self.telem.map_info.grid_info['ULHC_lat']
            
            URHC_lon = mapinfo.coord_coord(ULHC_lat, ULHC_lon, map_dim, 90)[1]
            URHC_lat = mapinfo.coord_coord(ULHC_lat, ULHC_lon, map_dim, 90)[0]
            
            LLHC_lon = mapinfo.coord_coord(ULHC_lat, ULHC_lon, map_dim, 180)[1]
            LLHC_lat = mapinfo.coord_coord(ULHC_lat, ULHC_lon, map_dim, 180)[0]
            
            LRHC_lon = mapinfo.coord_coord(LLHC_lat, LLHC_lon, map_dim, 90)[1]
            LRHC_lat = mapinfo.coord_coord(LLHC_lat, LLHC_lon, map_dim, 90)[0]
            
            if not image_name in os.listdir(TEXTURES_DIR):
                with open(TEXTURE_XML_TEMPLATE, 'r') as template:
                    contents = template.read()
                
                new_contents = contents.format(filename=image_name,
                                               LLHC_lon=LLHC_lon,
                                               LLHC_lat=LLHC_lat,
                                               LRHC_lon=LRHC_lon,
                                               LRHC_lat=LRHC_lat,
                                               URHC_lon=URHC_lon,
                                               URHC_lat=URHC_lat,
                                               ULHC_lon=ULHC_lon,
                                               ULHC_lat=ULHC_lat)
                
                if os.path.exists(TEXTURE_XML):
                    with open(TEXTURE_XML, 'r') as text_xml:
                        current_contents = text_xml.read()
                    
                    if current_contents:
                        if '\t</CustomTextureList>' in current_contents:
                            current_contents = current_contents.split('\t</CustomTextureList>')[0] + new_contents.split('<CustomTextureList>')[1]
                        
                            with open(TEXTURE_XML, 'w') as outFile:
                                outFile.write(current_contents)
                        
                        else:
                            with open(TEXTURE_XML, 'w') as outFile:
                                outFile.write(new_contents)
                        
                    else:
                        with open(TEXTURE_XML, 'w') as outFile:
                            outFile.write(new_contents)
                
                else:
                    with open(TEXTURE_XML, 'w') as outFile:
                        outFile.write(new_contents)
                
                src = mapinfo.MAP_PATH
                dst = os.path.join(TEXTURES_DIR, image_name)
                
                shutil.copy(src, dst)
    
    def setup_log(self):
        '''
        Description:
        ------------
        Instantiate a new ACMI log file
        '''
        
        self.loc_time = dt.datetime.now()
        self.title = TITLE_FORMAT.format(timestamp=self.loc_time.strftime('%Y_%m_%d_%H_%M_%S'), user=USERNAME)
        self.title = os.path.join(self.log_dir, self.title)
        
        self.logger.create(self.title)
        self.header_inserted = False
        self.meta_inserted   = False
    
    def process_player_data(self):
        '''
        Description:
        ------------
        Record/stream a single sample of user War Thunder telemetry data
        '''
        
        if self.telem.get_telemetry():
            # create a new log if player was dead but just now respawned
            if self.player_dead:
                self.setup_log()
                self.player_dead = False
            
            # insert header in ACMI file
            if not self.header_inserted and self.telem.map_info.map_valid:
                header = format_header_dict(self.telem.map_info.grid_info, self.loc_time)
                self.logger.insert_user_header(header)
                self.header_inserted = True
            
            # insert telemetry sample in ACMI file
            if self.header_inserted:
                if not self.meta_inserted:
                    entry = format_entry_dict(self.telem.full_telemetry,
                                              team_flag=self.team,
                                              initial_entry=True)
                    self.meta_inserted = True
                else:
                    entry = format_entry_dict(self.telem.full_telemetry,
                                              team_flag=self.team)
                self.logger.insert_entry(0, entry)
            
            log_line = self.logger.format_entry(0, entry)
            
            # report telemetry to MQTT broker
            if self.mqtt_enable:
                mqtt_payload = json.dumps({'player':   USERNAME,
                                           'ref_time': self.logger.reference_time.isoformat(),
                                           'entry':    log_line})
                self.mqttc.publish(self.mqtt_id, mqtt_payload)
            
            # report telemetry to Tacview
            if self.stream_enable:
                self.send_data.emit(log_line)
            
            # report telemetry to USB device
            if self.usb_enable:
                try:
                    self.send_usb_telem()
                except ValueError:
                    import traceback
                    traceback.print_exc()
                    print('ERROR: Could not communicate with USB device - Ending USB streaming')
                    self.usb_enable = False
            
            # save match map as a custom texture in Tacview
            if os.path.exists(TEXTURES_DIR):
                self.save_texture_files()
        
        # identify when the player has died
        elif not self.telem.map_info.player_found:
            self.player_dead = True
        
    def run(self):
        '''
        Description:
        ------------
        Main thread to record/stream user data
        '''
        
        self.player_dead = True
        
        sample_baseline = dt.datetime.now()
        now             = dt.datetime.now()
        
        self.setup_log()
        self.init_mqtt_struct()
        
        while True:
            if not os.path.exists(REF_FILE):
                self.init_mqtt_struct()
            
            now = dt.datetime.now()
            time_dif = (now - sample_baseline).total_seconds()
            
            if time_dif >= self.sample_period:
                sample_baseline += dt.timedelta(seconds=time_dif)
                self.process_player_data()


class StreamThread(QThread):
    '''
    Description:
    ------------
    Thread class used to stream personal and remote player match data via a
    localhost TCP connection with Tacview
    '''
    
    def __init__(self, parent=None):
        super(StreamThread, self).__init__(parent)
        self.port = parent.ui.live_telem_port.value()
        self.MAX_BUFF_LEN = 100
        
    def run(self):
        try:
            self.server = TCPServer(('localhost', self.port), StreamHandler)
            self.server.serve_forever()
        except OSError:
            print('ERROR: TCP port in use - please pick a different port')



class StreamHandler(BaseRequestHandler):
    '''
    Description:
    ------------
    Stream personal and remote player match data via a localhost TCP connection
    with Tacview
    '''
    
    MAX_BUFF_LEN     = 100
    remote_data_buff = []
    
    def handle(self):
        self.request.sendall(b'XtraLib.Stream.0\nTacview.RealTimeTelemetry.0\nThunder_Viewer\n\x00')
        self.data = self.request.recv(1024).strip()
        self.read_index = 0
        
        init_str = acmi.header_mandatory.format(filetype='text/acmi/tacview',
                                                acmiver='2.1',
                                                reftime=dt.datetime.utcnow().isoformat())
        
        try:
            payload = bytes(init_str, encoding='utf8')
            self.request.sendall(payload)
        except ConnectionAbortedError:
            print('Tacview closed live-telemetry connection')
            return
        
        while True:
            # clear out buffer in case of memory leak
            if len(self.remote_data_buff) > self.MAX_BUFF_LEN:
                self.remote_data_buff = []
            
            if self.remote_data_buff:
                # process and clear input buffer
                for index in range(len(self.remote_data_buff)-1, -1, -1):
                    try:
                        payload = bytes(self.remote_data_buff[index], encoding='utf8')
                        self.request.sendall(payload)
                    except ConnectionAbortedError:
                        print('Tacview closed live-telemetry connection')
                        return
                    
                    self.remote_data_buff.pop(index)


class MqttSubThread(QThread):
    '''
    Description:
    ------------
    Thread class used to download remote user's data via MQTT
    '''
    
    update_names = pyqtSignal(list)
    send_data = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super(MqttSubThread, self).__init__(parent)
        
        self.stream_enable = parent.ui.live_telem.isChecked()
        self.mqtt_enable   = True
        self.mqtt_id       = parent.ui.mqtt_id.text()
        self.mqttc         = mqtt.Client()
        self.mqttc.on_connect = self.on_connect
        self.mqttc.on_message = self.on_message
        self.remote_players   = {}
        self.ids_in_use       = []
        self.blocked_players  = []
        
        if self.mqttc.connect(BROKER_HOST):
            print('ERROR: Could not connect to MQTT broker {}'.format(BROKER_HOST))
            self.mqtt_enable = False
    
    def on_connect(self, client, userdata, flags, rc):
        '''
        Description:
        ------------
        Callback function - subscribe to all MQTT messages where the topic is
        the remote session ID specified in the GUI
        '''
        
        client.subscribe(topic=self.mqtt_id)
    
    def on_message(self, client, userdata, message):
        '''
        Description:
        ------------
        Callback function - process remote player's data (record/stream)
        '''
        
        try:
            payload = json.loads(message.payload)
            
            # only process remote player's data
            if not payload['player'] == USERNAME:
                with open(REF_FILE, 'r') as f:
                    user_tref   = dt.datetime.strptime(f.readline().replace('\n', ''), TIME_FORMAT)
                    user_obj_id = f.readline()
                    
                if user_obj_id not in self.ids_in_use:
                    self.ids_in_use.append(user_obj_id)
                
                remote_tref   = dt.datetime.strptime(payload['ref_time'], TIME_FORMAT)
                remote_tstamp = float(payload['entry'].split('\n')[0].replace('#', ''))
                remote_tstamp_str = str(remote_tstamp)
                
                # adjust remote user's timestamp to local user's reference time
                sample_dt   = remote_tref + dt.timedelta(seconds=remote_tstamp)
                true_tstamp = '{:0.2f}'.format((sample_dt - user_tref).total_seconds())
                payload['entry'].replace(remote_tstamp_str, true_tstamp)
                
                # process players new to the remote session
                if payload['player'] not in self.remote_players.keys():
                    loc_time = dt.datetime.now()
                    title = TITLE_FORMAT.format(timestamp=loc_time.strftime('%Y_%m_%d_%H_%M_%S'), user=payload['player'])
                    title = os.path.join(REMOTE_DIR, title)
                    
                    self.remote_players[payload['player']] = {'logger': None}
                    self.remote_players[payload['player']]['logger'] = acmi.ACMI()
                    self.remote_players[payload['player']]['logger'].create(title)
                    self.remote_players[payload['player']]['log_path'] = title
                    self.remote_players[payload['player']]['obj_id']   = gen_id()
                    
                    # make sure new object ID is unique accross all objects
                    while self.remote_players[payload['player']]['obj_id'] in self.ids_in_use:
                        self.remote_players[payload['player']]['obj_id'] = gen_id()
                    
                    self.ids_in_use.append(self.remote_players.keys())
                    self.update_names.emit(self.remote_players.keys())
                
                # stream remote session data to Tacview if enabled and player isn't blocked
                if self.stream_enable and (payload['player'] not in self.blocked_players):
                    self.send_data.emit(payload['entry'])

                try:
                    # log remote player's data in ACMI file
                    with open(self.remote_players[payload['player']]['log_path'], 'a') as log:
                        log.write(payload['entry'])
                except FileNotFoundError:
                    print('ERROR: Could not find remote user log file')
                
        except:
            import traceback
            traceback.print_exc()
    
    def run(self):
        '''
        Description:
        ------------
        Thread used to process all MQTT messages for the remote session
        '''
        
        if self.mqtt_enable:
            self.mqttc.loop_forever()


def main():
    '''
    Description:
    ------------
    Main program to run
    '''
    
    app = QApplication(sys.argv)
    w   = AppWindow()
    w.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    try:
        main()
    except (SystemExit, KeyboardInterrupt, requests.exceptions.ConnectionError):
        pass


