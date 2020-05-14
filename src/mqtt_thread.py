import os
import json
import datetime as dt
import paho.mqtt.client as mqtt
from random import randint
from WarThunder import acmi
from PyQt5.QtCore import QThread, pyqtSignal
from constants import USERNAME, BROKER_HOST, TIME_FORMAT
from constants import TITLE_FORMAT, REF_FILE, REMOTE_DIR


def gen_id():
    '''
    Description:
    ------------
    Find a valid Tacview object hex ID
    
    :return: str - new object hex ID
    '''
    
    return str(hex(randint(1, acmi.MAX_NUM_OBJS + 2))[2:]).upper()


class MqttSubThread(QThread):
    '''
    Description:
    ------------
    Thread class used to download remote user's data via MQTT
    '''
    
    update_names = pyqtSignal(list)
    send_stream_data = pyqtSignal(str)
    
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
                    self.send_stream_data.emit(payload['entry'])

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