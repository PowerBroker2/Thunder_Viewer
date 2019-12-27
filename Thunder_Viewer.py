import os
import sys
import json
import arrow
import requests
import datetime as dt
import paho.mqtt.client as mqtt
from getpass import getuser
from socketserver import TCPServer, BaseRequestHandler
from PyQt5.QtCore import QThread, QProcess
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
from pySerialTransfer import pySerialTransfer as transfer
from pySerialTransfer.pySerialTransfer import msb, lsb, byte_val
from WarThunder import general, telemetry, acmi
from WarThunder.telemetry import combine_dicts
from gui import Ui_ThunderViewer


USERNAME     = getuser()
BROKER_HOST  = 'broker.hivemq.com'
APP_DIR      = os.path.dirname(os.path.realpath(__file__))
STREAM_DIR   = os.path.join(APP_DIR, 'stream_log')
STREAM_FILE  = os.path.join(STREAM_DIR, 'stream.acmi')
LOGS_DIR     = os.path.join(APP_DIR, 'logs')
MQTT_DIR     = os.path.join(APP_DIR, 'mqtt')
REMOTE_DIR   = os.path.join(MQTT_DIR, 'remote_players')
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

def format_entry_dict(telem, initial_entry=False):
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
                                        format_init_meta(telem))
    
    return formatted_entry

def format_init_meta(telem):
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
    
    return formatted_meta


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
        
        self.connect_signals()
        self.init_recording_status()
        self.update_port_list()
        
        self.ui.acmi_path.setText(LOGS_DIR)
        self.ui.usb_baud.setCurrentIndex(8) # default baud of 115200
    
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
        self.ui.port_refresh.clicked.connect(self.update_port_list)
    
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
        TODO
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
        TODO
        '''
        
        if not self.ui.recording.isChecked():
            self.disable_inputs()
            
            if self.ui.mqtt.isChecked():
                self.mqtt_sub_th = MqttSubThread()
                self.mqtt_sub_th.start()
            
            if self.ui.live_telem.isChecked():
                self.stream_th = StreamThread(self)
                self.stream_th.start()
            
            self.rec_th = RecordThread(self)
            self.rec_th.start()
            self.ui.recording.setChecked(True)
    
    def stop_recording_data(self):
        '''
        Description:
        ------------
        TODO
        '''
        
        self.enable_inputs()
        
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
        TODO
        '''
        
        self.ui.recording.setDisabled(True)
        self.ui.recording.setChecked(False)
    
    def update_port_list(self):
        '''
        Description:
        ------------
        TODO
        '''
        
        ports = transfer.open_ports()
        self.ui.usb_ports.clear()
        self.ui.usb_ports.addItems(ports)
    
    def enable_inputs(self):
        self.change_inputs(True)
    
    def disable_inputs(self):
        self.change_inputs(False)
    
    def change_inputs(self, enable):
        '''
        Description:
        ------------
        TODO
        '''
        
        self.ui.tacview_path.setEnabled(enable)
        self.ui.tacview_select.setEnabled(enable)
        self.ui.acmi_path.setEnabled(enable)
        self.ui.acmi_select.setEnabled(enable)
        self.ui.live_telem.setEnabled(enable)
        self.ui.live_telem_port.setEnabled(enable)
        self.ui.mqtt.setEnabled(enable)
        self.ui.mqtt_id.setEnabled(enable)
        self.ui.usb_ports.setEnabled(enable)
        self.ui.live_usb.setEnabled(enable)


class RecordThread(QThread):
    '''
    Description:
    ------------
    TODO
    '''
    
    def __init__(self, parent=None):
        super(RecordThread, self).__init__(parent)
        
        self.telem   = telemetry.TelemInterface() # class used to query War Thunder telemetry
        self.logger  = acmi.ACMI()                # class used to log match data
        self.log_dir = parent.ui.acmi_path.text()
        self.mqtt_enable   = parent.ui.mqtt.isChecked()
        self.stream_enable = parent.ui.live_telem.isChecked()
        self.usb_enable    = parent.ui.live_usb.isChecked()
        
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
        
        if self.usb_enable:
            self.usb_port = parent.ui.live_usb.text()
            self.usb_baud = parent.ui.usb_baud.text()
            
            if not self.usb_port:
                self.usb_enable = False
            else:
                self.transfer = transfer.SerialTransfer(self.usb_port, self.usb_baud)
    
    def send_usb_telem(self):
        '''
        Description:
        ------------
        TODO
        '''
        
        # mulitply float values by a constant so as to preserve as much
        # of the value's precision as possible
        pitch = int(self.telem.basic_telemetry['pitch'] * 350)
        roll  = int(self.telem.basic_telemetry['roll']  * 350)
        hdg   = int(self.telem.basic_telemetry['heading'])
        alt   = int(self.telem.basic_telemetry['altitude'])
        lat   = int(self.telem.basic_telemetry['lat'] * 5000)
        lon   = int(self.telem.basic_telemetry['lon'] * 5000)
        
        self.transfer.txBuff[0]  = msb(pitch)
        self.transfer.txBuff[1]  = lsb(pitch)
        self.transfer.txBuff[2]  = msb(roll)
        self.transfer.txBuff[3]  = lsb(roll)
        self.transfer.txBuff[4]  = msb(hdg)
        self.transfer.txBuff[5]  = lsb(hdg)
        self.transfer.txBuff[6]  = msb(alt)
        self.transfer.txBuff[7]  = lsb(alt)
        self.transfer.txBuff[8]  = msb(lat)
        self.transfer.txBuff[9]  = byte_val(lat, 2)
        self.transfer.txBuff[10] = byte_val(lat, 1)
        self.transfer.txBuff[11] = lsb(lat)
        self.transfer.txBuff[12] = msb(lon)
        self.transfer.txBuff[13] = byte_val(lon, 2)
        self.transfer.txBuff[14] = byte_val(lon, 1)
        self.transfer.txBuff[15] = lsb(lon)
        
        self.transfer.send(16)
    
    def process_player_data(self):
        '''
        Description:
        ------------
        TODO
        '''
        
        if self.telem.get_telemetry():
            if not self.header_inserted and self.telem.map_info.map_valid:
                header = format_header_dict(self.telem.map_info.grid_info, self.loc_time)
                self.logger.insert_user_header(header)
                self.header_inserted = True
            
            if self.header_inserted:
                if not self.meta_inserted:
                    entry = format_entry_dict(self.telem.full_telemetry, True)
                    self.meta_inserted = True
                else:
                    entry = format_entry_dict(self.telem.full_telemetry)
                self.logger.insert_entry(0, entry)
            
            log_line = self.logger.format_entry(0, entry)
            
            if self.mqtt_enable:
                mqtt_payload = json.dumps({'player':   USERNAME,
                                           'ref_time': self.logger.reference_time,
                                           'entry':    log_line})
                self.mqttc.publish(self.mqtt_id, mqtt_payload,)
            
            if self.stream_enable:
                if not os.path.exists(STREAM_FILE):
                    if not os.path.exists(STREAM_DIR):
                        os.makedirs(STREAM_DIR)
                    init_stream_log()
                
                with open(STREAM_FILE, 'a') as log:
                    log.write(log_line)
            
            if self.usb_enable:
                self.send_usb_telem()
        
    def run(self):
        '''
        Description:
        ------------
        TODO
        '''
        
        self.loc_time = dt.datetime.now()
        self.title = TITLE_FORMAT.format(timestamp=self.loc_time.strftime('%Y_%m_%d_%H_%M_%S'), user=USERNAME)
        self.title = os.path.join(self.log_dir, self.title)
        
        self.logger.create(self.title)
        self.header_inserted = False
        self.meta_inserted   = False
        
        while True:
            self.process_player_data()


class StreamThread(QThread):
    '''
    Description:
    ------------
    TODO
    '''
    
    def __init__(self, parent=None):
        super(StreamThread, self).__init__(parent)
        self.port = parent.ui.live_telem_port.value()
        
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
    TODO
    '''
    
    def handle(self):
        self.request.sendall(b'XtraLib.Stream.0\nTacview.RealTimeTelemetry.0\nThunder_Viewer\n\x00')
        self.data = self.request.recv(1024).strip()
        self.read_index = 0
        
        if not os.path.exists(STREAM_DIR):
            os.makedirs(STREAM_DIR)
        init_stream_log()
        
        while True:
            if os.path.exists(STREAM_FILE):
                try:
                    with open(STREAM_FILE, 'r') as f:
                        log_line = f.readlines()[self.read_index]
                except (FileNotFoundError, IndexError):
                    log_line = ''
                
                if log_line:
                    try:
                        payload = bytes(log_line, encoding='utf8')
                        self.request.sendall(payload)
                        self.read_index += 1
                    except ConnectionAbortedError:
                        print('Tacview closed live-telemetry connection')
                        init_stream_log()
                        return
            else:
                if not os.path.exists(STREAM_DIR):
                    os.makedirs(STREAM_DIR)
                self.read_index = 0
                init_stream_log()


#copy reference time to compare to incoming timestamps
class MqttSubThread(QThread):
    '''
    Description:
    ------------
    TODO
    '''
    
    def __init__(self, parent=None):
        super(MqttSubThread, self).__init__(parent)
        
        self.mqtt_enable = True
        self.mqtt_id     = parent.ui.mqtt_id.text()
        self.mqttc       = mqtt.Client()
        self.mqttc.on_connect = self.on_connect
        self.mqttc.on_message = self.on_message
        
        if self.mqttc.connect(BROKER_HOST):
            print('ERROR: Could not connect to MQTT broker {}'.format(BROKER_HOST))
            self.mqtt_enable = False
    
    def on_connect(self, client, userdata, flags, rc):
    	client.subscribe(topic=self.mqtt_id)
    
    def on_message(self, client, userdata, message):
    	print('------------------------------')
    	print('topic: %s' % message.topic)
    	print('payload: %s' % message.payload)
    
    def run(self):
        if self.mqtt_enable:
            self.mqttc.loop_forever()


def main():
    '''
    Description:
    ------------
    TODO
    '''
    
    app = QApplication(sys.argv)
    w = AppWindow()
    w.show()
    sys.exit(app.exec_())

def init_stream_log():
    '''
    Description:
    ------------
    TODO
    '''
    
    with open(STREAM_FILE, 'w') as log:
        log.write(acmi.header_mandatory.format(filetype='text/acmi/tacview',
                                               acmiver='2.1',
                                               reftime=str(arrow.utcnow()).split('+')[0]))

def garbage_collection():
    '''
    Description:
    ------------
    TODO
    '''
    
    init_stream_log()


if __name__ == "__main__":
    try:
        main()
    except (SystemExit, KeyboardInterrupt, requests.exceptions.ConnectionError):
        garbage_collection()



