import os
import json
import shutil
import struct
import datetime as dt
import paho.mqtt.client as mqtt
from PyQt5.QtCore import QThread, pyqtSignal
from WarThunder import general, telemetry, acmi, mapinfo
from WarThunder.telemetry import combine_dicts
from constants import USERNAME, BROKER_HOST
from constants import REMOTE_DIR, REF_FILE, TEXTURES_DIR
from constants import TEXTURE_XML_TEMPLATE, TEXTURE_XML, TITLE_FORMAT
from constants import ACMI_HEADER, ACMI_ENTRY, INITIAL_META


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
    formatted_header['Author']             = USERNAME
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
    
    try:
        formatted_entry['RollControlInput']  = '{0:.6f}'.format(telem['stick_ailerons'])
    except KeyError:
        formatted_entry['RollControlInput']  = 0
        
    try:
        formatted_entry['PitchControlInput'] = '{0:.6f}'.format(telem['stick_elevator'])
    except KeyError:
        formatted_entry['PitchControlInput'] = 0
    
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


class RecordThread(QThread):
    '''
    Description:
    ------------
    Thread class used to record and stream personal match data
    '''
    
    send_stream_data = pyqtSignal(str)
    send_overlay_data = pyqtSignal(dict)
    
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
            
            # report telemetry to overlay
            self.send_overlay_data.emit(self.telem.full_telemetry)
            
            # report telemetry to MQTT broker
            if self.mqtt_enable:
                mqtt_payload = json.dumps({'player':   USERNAME,
                                           'ref_time': self.logger.reference_time.isoformat(),
                                           'entry':    log_line})
                self.mqttc.publish(self.mqtt_id, mqtt_payload)
            
            # report telemetry to Tacview
            if self.stream_enable:
                self.send_stream_data.emit(log_line)
            
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