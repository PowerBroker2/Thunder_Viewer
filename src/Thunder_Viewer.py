import os
import sys
import requests
from PyQt5.QtGui import QColor
from PyQt5.QtCore import QProcess, pyqtSlot, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QTableWidgetItem
from pySerialTransfer import pySerialTransfer as transfer
from gui.remotePlayGui import Ui_PlayerManager
from gui.usbFieldsGui import Ui_usbFieldManager
from gui.gui import Ui_ThunderViewer
from gui.overlay import Ui_Overlay
from mqtt_thread import MqttSubThread
from stream_thread import StreamThread, StreamHandler
from record_thread import RecordThread
from constants import APP_DIR, LOGS_DIR


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
        
        self.setup_overlay()
        self.setup_player_manager()
        self.setup_usb_manager()
        
        self.connect_signals()
        self.init_recording_status()
        self.update_port_list()
        
        self.ui.acmi_path.setText(LOGS_DIR)
        self.enable_inputs()
        self.find_tacview_install()
        
        self.player_names = []
    
    def setup_overlay(self):
        '''
        Description:
        ------------
        TODO
        '''
        
        self.Overlay = QMainWindow()
        self.Overlay_ui = Ui_Overlay()
        self.Overlay_ui.setupUi(self.Overlay)
        
        self.Overlay.setWindowFlags(Qt.WindowStaysOnTopHint |
                                    Qt.FramelessWindowHint  |
                                    Qt.X11BypassWindowManagerHint)
        self.Overlay.setAttribute(Qt.WA_TranslucentBackground)
        
        self.Overlay_ui.telem_table.setStyleSheet("QTableWidget {background-color: transparent;}"
                                                  "QHeaderView::section {background-color: transparent;}"
                                                  "QHeaderView {background-color: transparent;}"
                                                  "QTableCornerButton::section {background-color: transparent;}")
        self.Overlay_ui.telem_table.setColumnCount(3)
        self.Overlay_ui.telem_table.setRowCount(1)
        self.Overlay_ui.field_select_table.setColumnCount(1)
        self.Overlay_ui.field_select_table.setRowCount(0)
        self.Overlay.move(0, 0)
        
        self.overlay_fields = []
        
    def setup_player_manager(self):
        '''
        Description:
        ------------
        TODO
        '''
        
        self.PlayerManager = QMainWindow()
        self.PlayerManager_ui = Ui_PlayerManager()
        self.PlayerManager_ui.setupUi(self.PlayerManager)
    
    def setup_usb_manager(self):
        '''
        Description:
        ------------
        TODO
        '''
        
        self.UsbManager = QMainWindow()
        self.UsbManager_ui = Ui_usbFieldManager()
        self.UsbManager_ui.setupUi(self.UsbManager)
    
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
        self.ui.manage_usb_fields.clicked.connect(self.UsbManager.show)
        self.UsbManager_ui.apply.clicked.connect(self.update_usb_fields)
        self.ui.port_refresh.clicked.connect(self.update_port_list)
        self.ui.launch_overlay.clicked.connect(self.Overlay.showFullScreen)
        self.Overlay_ui.close_button.clicked.connect(self.Overlay.close)
        
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
                self.mqtt_sub_th.send_stream_data.connect(self.send_to_stream)
            
            if self.ui.live_telem.isChecked():
                self.stream_th = StreamThread(self)
                self.stream_th.start()
            
            self.rec_th = RecordThread(self)
            self.rec_th.start()
            self.rec_th.send_stream_data.connect(self.send_to_stream)
            self.rec_th.send_overlay_data.connect(self.update_overlay)
            
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
    
    @pyqtSlot(list)
    def update_player_names(self, names):
        self.player_names = names
    
    @pyqtSlot(str)
    def send_to_stream(self, line):
        try:
            StreamHandler.remote_data_buff.append(line)
        except AttributeError:
            pass
    
    @pyqtSlot(dict)
    def update_overlay(self, telem_dict):
        # find all valid fields
        found_fields = telem_dict.keys()
        
        # remove any fields that are no longer valid
        for i in range(len(self.overlay_fields)-1, -1, -1):
            if self.overlay_fields[i] not in found_fields:
                for row in range(self.Overlay_ui.field_select_table.rowCount()):
                    field = self.Overlay_ui.field_select_table.item(row, 0).text()
                    
                    scrubbed_field = self.overlay_fields[i].replace('_', ' ').upper().split(',')[0]
                    if field == scrubbed_field:
                        self.Overlay_ui.field_select_table.removeRow(row)
                        break
                
                self.overlay_fields.pop(i)
        
        # add new fields
        for field in found_fields:
            if field not in self.overlay_fields:
                self.overlay_fields.append(field)
                
                #add row
                new_row_num = self.Overlay_ui.field_select_table.rowCount()
                self.Overlay_ui.field_select_table.insertRow(new_row_num)
                
                chkBoxItem = QTableWidgetItem()
                chkBoxItem.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
                chkBoxItem.setCheckState(Qt.Unchecked)
                chkBoxItem.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                chkBoxItem.setText(field.replace('_', ' ').upper().split(',')[0])
                
                self.Overlay_ui.field_select_table.setItem(new_row_num, 0, chkBoxItem)
                
        selected_fields_list = []
        for row in range(self.Overlay_ui.field_select_table.rowCount()):
            try:
                if self.Overlay_ui.field_select_table.item(row, 0).checkState():
                    selected_fields_list.append(self.Overlay_ui.field_select_table.item(row, 0).text())
            except AttributeError:
                pass
        
        # reset table
        self.Overlay_ui.telem_table.setRowCount(0)
        
        # fill the table with new telemetry data
        index = 0
        for datum in telem_dict.keys():
            datum_str = datum.replace('_', ' ').upper().split(',')[0]
            
            if datum_str in selected_fields_list:
                self.Overlay_ui.telem_table.insertRow(index)
                self.Overlay_ui.telem_table.setItem(index, 0, QTableWidgetItem(datum_str + '   '))
                self.Overlay_ui.telem_table.setItem(index, 1, QTableWidgetItem(str(telem_dict[datum]).upper()))
                index += 1
        
        # apply font color to each cell
        for row in range(self.Overlay_ui.telem_table.rowCount()):
            for col in range(self.Overlay_ui.telem_table.columnCount()):
                try:
                    self.Overlay_ui.telem_table.item(row, col).setForeground(QColor(255, 255, 255))
                except AttributeError:
                    pass
        
        # resize table to contents
        self.Overlay_ui.telem_table.resizeColumnsToContents()
        self.Overlay_ui.telem_table.resizeRowsToContents()
        self.Overlay_ui.telem_table.resize(10000, 10000)
    
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



