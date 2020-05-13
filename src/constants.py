import os
from getpass import getuser


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
