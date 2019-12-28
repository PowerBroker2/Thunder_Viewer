# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'gui.ui'
#
# Created by: PyQt5 UI code generator 5.12.3
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_ThunderViewer(object):
    def setupUi(self, ThunderViewer):
        ThunderViewer.setObjectName("ThunderViewer")
        ThunderViewer.resize(500, 735)
        ThunderViewer.setMinimumSize(QtCore.QSize(500, 735))
        ThunderViewer.setMaximumSize(QtCore.QSize(500, 735))
        self.centralwidget = QtWidgets.QWidget(ThunderViewer)
        self.centralwidget.setObjectName("centralwidget")
        self.mqtt_id = QtWidgets.QLineEdit(self.centralwidget)
        self.mqtt_id.setGeometry(QtCore.QRect(260, 240, 201, 20))
        self.mqtt_id.setObjectName("mqtt_id")
        self.recording = QtWidgets.QRadioButton(self.centralwidget)
        self.recording.setGeometry(QtCore.QRect(90, 650, 82, 17))
        self.recording.setObjectName("recording")
        self.record = QtWidgets.QPushButton(self.centralwidget)
        self.record.setGeometry(QtCore.QRect(260, 630, 201, 23))
        self.record.setObjectName("record")
        self.stop = QtWidgets.QPushButton(self.centralwidget)
        self.stop.setGeometry(QtCore.QRect(260, 660, 201, 23))
        self.stop.setObjectName("stop")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(260, 220, 201, 16))
        self.label_2.setObjectName("label_2")
        self.mqtt = QtWidgets.QCheckBox(self.centralwidget)
        self.mqtt.setGeometry(QtCore.QRect(50, 240, 191, 17))
        self.mqtt.setObjectName("mqtt")
        self.acmi_select = QtWidgets.QPushButton(self.centralwidget)
        self.acmi_select.setGeometry(QtCore.QRect(40, 60, 101, 23))
        self.acmi_select.setObjectName("acmi_select")
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(260, 130, 201, 20))
        self.label_3.setObjectName("label_3")
        self.live_telem = QtWidgets.QCheckBox(self.centralwidget)
        self.live_telem.setGeometry(QtCore.QRect(50, 150, 191, 20))
        self.live_telem.setObjectName("live_telem")
        self.launch_tacview_live = QtWidgets.QPushButton(self.centralwidget)
        self.launch_tacview_live.setGeometry(QtCore.QRect(40, 510, 421, 31))
        self.launch_tacview_live.setObjectName("launch_tacview_live")
        self.tacview_select = QtWidgets.QPushButton(self.centralwidget)
        self.tacview_select.setGeometry(QtCore.QRect(40, 20, 101, 23))
        self.tacview_select.setObjectName("tacview_select")
        self.live_telem_port = QtWidgets.QSpinBox(self.centralwidget)
        self.live_telem_port.setGeometry(QtCore.QRect(260, 150, 201, 22))
        self.live_telem_port.setMaximum(9999)
        self.live_telem_port.setProperty("value", 8110)
        self.live_telem_port.setObjectName("live_telem_port")
        self.tacview_path = QtWidgets.QLineEdit(self.centralwidget)
        self.tacview_path.setGeometry(QtCore.QRect(150, 20, 311, 20))
        self.tacview_path.setReadOnly(True)
        self.tacview_path.setObjectName("tacview_path")
        self.acmi_path = QtWidgets.QLineEdit(self.centralwidget)
        self.acmi_path.setGeometry(QtCore.QRect(150, 60, 311, 20))
        self.acmi_path.setReadOnly(True)
        self.acmi_path.setObjectName("acmi_path")
        self.live_usb = QtWidgets.QCheckBox(self.centralwidget)
        self.live_usb.setGeometry(QtCore.QRect(50, 380, 181, 20))
        self.live_usb.setObjectName("live_usb")
        self.label_4 = QtWidgets.QLabel(self.centralwidget)
        self.label_4.setGeometry(QtCore.QRect(260, 320, 201, 20))
        self.label_4.setObjectName("label_4")
        self.usb_ports = QtWidgets.QComboBox(self.centralwidget)
        self.usb_ports.setGeometry(QtCore.QRect(260, 340, 201, 22))
        self.usb_ports.setObjectName("usb_ports")
        self.port_refresh = QtWidgets.QPushButton(self.centralwidget)
        self.port_refresh.setGeometry(QtCore.QRect(260, 380, 201, 23))
        self.port_refresh.setObjectName("port_refresh")
        self.usb_baud = QtWidgets.QComboBox(self.centralwidget)
        self.usb_baud.setGeometry(QtCore.QRect(260, 430, 201, 22))
        self.usb_baud.setObjectName("usb_baud")
        self.usb_baud.addItem("")
        self.usb_baud.addItem("")
        self.usb_baud.addItem("")
        self.usb_baud.addItem("")
        self.usb_baud.addItem("")
        self.usb_baud.addItem("")
        self.usb_baud.addItem("")
        self.usb_baud.addItem("")
        self.usb_baud.addItem("")
        self.usb_baud.addItem("")
        self.usb_baud.addItem("")
        self.usb_baud.addItem("")
        self.usb_baud.addItem("")
        self.usb_baud.addItem("")
        self.usb_baud.addItem("")
        self.usb_baud.addItem("")
        self.usb_baud.addItem("")
        self.usb_baud.addItem("")
        self.label_5 = QtWidgets.QLabel(self.centralwidget)
        self.label_5.setGeometry(QtCore.QRect(260, 410, 201, 20))
        self.label_5.setObjectName("label_5")
        self.line = QtWidgets.QFrame(self.centralwidget)
        self.line.setGeometry(QtCore.QRect(20, 290, 461, 20))
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.line_2 = QtWidgets.QFrame(self.centralwidget)
        self.line_2.setGeometry(QtCore.QRect(20, 100, 461, 20))
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.line_3 = QtWidgets.QFrame(self.centralwidget)
        self.line_3.setGeometry(QtCore.QRect(20, 470, 461, 20))
        self.line_3.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_3.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_3.setObjectName("line_3")
        self.line_4 = QtWidgets.QFrame(self.centralwidget)
        self.line_4.setGeometry(QtCore.QRect(20, 190, 461, 20))
        self.line_4.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_4.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_4.setObjectName("line_4")
        self.team = QtWidgets.QComboBox(self.centralwidget)
        self.team.setGeometry(QtCore.QRect(260, 580, 201, 22))
        self.team.setObjectName("team")
        self.team.addItem("")
        self.team.addItem("")
        self.label_6 = QtWidgets.QLabel(self.centralwidget)
        self.label_6.setGeometry(QtCore.QRect(260, 560, 201, 16))
        self.label_6.setObjectName("label_6")
        ThunderViewer.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(ThunderViewer)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 500, 21))
        self.menubar.setObjectName("menubar")
        ThunderViewer.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(ThunderViewer)
        self.statusbar.setObjectName("statusbar")
        ThunderViewer.setStatusBar(self.statusbar)

        self.retranslateUi(ThunderViewer)
        self.usb_baud.setCurrentIndex(8)
        QtCore.QMetaObject.connectSlotsByName(ThunderViewer)

    def retranslateUi(self, ThunderViewer):
        _translate = QtCore.QCoreApplication.translate
        ThunderViewer.setWindowTitle(_translate("ThunderViewer", "Thunder Viewer"))
        self.mqtt_id.setText(_translate("ThunderViewer", "FlightViewer"))
        self.recording.setText(_translate("ThunderViewer", "Recording"))
        self.record.setText(_translate("ThunderViewer", "Record"))
        self.stop.setText(_translate("ThunderViewer", "Stop"))
        self.label_2.setText(_translate("ThunderViewer", "Remote Session ID"))
        self.mqtt.setText(_translate("ThunderViewer", "Remote Session Enabled"))
        self.acmi_select.setText(_translate("ThunderViewer", "ACMI Directory:"))
        self.label_3.setText(_translate("ThunderViewer", "Live Tacview Telemetry Port"))
        self.live_telem.setText(_translate("ThunderViewer", "Tacview Streaming Enabled"))
        self.launch_tacview_live.setText(_translate("ThunderViewer", "Launch TacView for Live Telemetry"))
        self.tacview_select.setText(_translate("ThunderViewer", "Tacview Install:"))
        self.tacview_path.setText(_translate("ThunderViewer", "C:\\Program Files (x86)\\Tacview\\Tacview64.exe"))
        self.live_usb.setText(_translate("ThunderViewer", "USB Streaming Enabled"))
        self.label_4.setText(_translate("ThunderViewer", "Live USB Telemetry Port (COM)"))
        self.port_refresh.setText(_translate("ThunderViewer", "Refresh Port List"))
        self.usb_baud.setCurrentText(_translate("ThunderViewer", "115200"))
        self.usb_baud.setItemText(0, _translate("ThunderViewer", "4608000"))
        self.usb_baud.setItemText(1, _translate("ThunderViewer", "2000000"))
        self.usb_baud.setItemText(2, _translate("ThunderViewer", "1000000"))
        self.usb_baud.setItemText(3, _translate("ThunderViewer", "921600"))
        self.usb_baud.setItemText(4, _translate("ThunderViewer", "500000"))
        self.usb_baud.setItemText(5, _translate("ThunderViewer", "460800"))
        self.usb_baud.setItemText(6, _translate("ThunderViewer", "250000"))
        self.usb_baud.setItemText(7, _translate("ThunderViewer", "230400"))
        self.usb_baud.setItemText(8, _translate("ThunderViewer", "115200"))
        self.usb_baud.setItemText(9, _translate("ThunderViewer", "57600"))
        self.usb_baud.setItemText(10, _translate("ThunderViewer", "38400"))
        self.usb_baud.setItemText(11, _translate("ThunderViewer", "31250"))
        self.usb_baud.setItemText(12, _translate("ThunderViewer", "19200"))
        self.usb_baud.setItemText(13, _translate("ThunderViewer", "9600"))
        self.usb_baud.setItemText(14, _translate("ThunderViewer", "4800"))
        self.usb_baud.setItemText(15, _translate("ThunderViewer", "2400"))
        self.usb_baud.setItemText(16, _translate("ThunderViewer", "1200"))
        self.usb_baud.setItemText(17, _translate("ThunderViewer", "300"))
        self.label_5.setText(_translate("ThunderViewer", "USB Port Baud"))
        self.team.setItemText(0, _translate("ThunderViewer", "Blue Team"))
        self.team.setItemText(1, _translate("ThunderViewer", "Red Team"))
        self.label_6.setText(_translate("ThunderViewer", "Team"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ThunderViewer = QtWidgets.QMainWindow()
    ui = Ui_ThunderViewer()
    ui.setupUi(ThunderViewer)
    ThunderViewer.show()
    sys.exit(app.exec_())
