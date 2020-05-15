import datetime as dt
from socketserver import TCPServer, BaseRequestHandler
from PyQt5.QtCore import QThread
from WarThunder import acmi


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