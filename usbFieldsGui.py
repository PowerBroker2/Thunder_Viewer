# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'usbFieldsGui.ui'
#
# Created by: PyQt5 UI code generator 5.12.3
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_usbFieldManager(object):
    def setupUi(self, usbFieldManager):
        usbFieldManager.setObjectName("usbFieldManager")
        usbFieldManager.resize(372, 281)
        self.centralwidget = QtWidgets.QWidget(usbFieldManager)
        self.centralwidget.setObjectName("centralwidget")
        self.usb_fields = QtWidgets.QListWidget(self.centralwidget)
        self.usb_fields.setGeometry(QtCore.QRect(90, 30, 201, 161))
        self.usb_fields.setAlternatingRowColors(True)
        self.usb_fields.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        self.usb_fields.setObjectName("usb_fields")
        item = QtWidgets.QListWidgetItem()
        self.usb_fields.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.usb_fields.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.usb_fields.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.usb_fields.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.usb_fields.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.usb_fields.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.usb_fields.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.usb_fields.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.usb_fields.addItem(item)
        self.label_7 = QtWidgets.QLabel(self.centralwidget)
        self.label_7.setGeometry(QtCore.QRect(90, 10, 201, 20))
        self.label_7.setObjectName("label_7")
        self.apply = QtWidgets.QPushButton(self.centralwidget)
        self.apply.setGeometry(QtCore.QRect(10, 210, 351, 23))
        self.apply.setObjectName("apply")
        usbFieldManager.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(usbFieldManager)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 372, 21))
        self.menubar.setObjectName("menubar")
        usbFieldManager.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(usbFieldManager)
        self.statusbar.setObjectName("statusbar")
        usbFieldManager.setStatusBar(self.statusbar)

        self.retranslateUi(usbFieldManager)
        QtCore.QMetaObject.connectSlotsByName(usbFieldManager)

    def retranslateUi(self, usbFieldManager):
        _translate = QtCore.QCoreApplication.translate
        usbFieldManager.setWindowTitle(_translate("usbFieldManager", "USB Field Manager"))
        self.usb_fields.setSortingEnabled(False)
        __sortingEnabled = self.usb_fields.isSortingEnabled()
        self.usb_fields.setSortingEnabled(False)
        item = self.usb_fields.item(0)
        item.setText(_translate("usbFieldManager", "Roll Angle"))
        item = self.usb_fields.item(1)
        item.setText(_translate("usbFieldManager", "Pitch Angle"))
        item = self.usb_fields.item(2)
        item.setText(_translate("usbFieldManager", "Heading"))
        item = self.usb_fields.item(3)
        item.setText(_translate("usbFieldManager", "Altitude (meters)"))
        item = self.usb_fields.item(4)
        item.setText(_translate("usbFieldManager", "Airspeed (km/h)"))
        item = self.usb_fields.item(5)
        item.setText(_translate("usbFieldManager", "Latitude (dd)"))
        item = self.usb_fields.item(6)
        item.setText(_translate("usbFieldManager", "Longitude (dd)"))
        item = self.usb_fields.item(7)
        item.setText(_translate("usbFieldManager", "Flap State"))
        item = self.usb_fields.item(8)
        item.setText(_translate("usbFieldManager", "Gear State"))
        self.usb_fields.setSortingEnabled(__sortingEnabled)
        self.label_7.setText(_translate("usbFieldManager", "Select values to stream"))
        self.apply.setText(_translate("usbFieldManager", "Apply"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    usbFieldManager = QtWidgets.QMainWindow()
    ui = Ui_usbFieldManager()
    ui.setupUi(usbFieldManager)
    usbFieldManager.show()
    sys.exit(app.exec_())
