# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'remotePlayGui.ui'
#
# Created by: PyQt5 UI code generator 5.12.3
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_PlayerManager(object):
    def setupUi(self, PlayerManager):
        PlayerManager.setObjectName("PlayerManager")
        PlayerManager.resize(421, 208)
        PlayerManager.setMinimumSize(QtCore.QSize(421, 208))
        PlayerManager.setMaximumSize(QtCore.QSize(421, 208))
        self.centralwidget = QtWidgets.QWidget(PlayerManager)
        self.centralwidget.setObjectName("centralwidget")
        self.apply = QtWidgets.QPushButton(self.centralwidget)
        self.apply.setGeometry(QtCore.QRect(10, 140, 401, 23))
        self.apply.setObjectName("apply")
        self.player_list = QtWidgets.QListWidget(self.centralwidget)
        self.player_list.setGeometry(QtCore.QRect(60, 20, 301, 101))
        self.player_list.setAlternatingRowColors(True)
        self.player_list.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        self.player_list.setObjectName("player_list")
        PlayerManager.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(PlayerManager)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 421, 21))
        self.menubar.setObjectName("menubar")
        PlayerManager.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(PlayerManager)
        self.statusbar.setObjectName("statusbar")
        PlayerManager.setStatusBar(self.statusbar)

        self.retranslateUi(PlayerManager)
        QtCore.QMetaObject.connectSlotsByName(PlayerManager)

    def retranslateUi(self, PlayerManager):
        _translate = QtCore.QCoreApplication.translate
        PlayerManager.setWindowTitle(_translate("PlayerManager", "Manage Remote Player Data"))
        self.apply.setText(_translate("PlayerManager", "Apply"))
        self.player_list.setSortingEnabled(False)


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    PlayerManager = QtWidgets.QMainWindow()
    ui = Ui_PlayerManager()
    ui.setupUi(PlayerManager)
    PlayerManager.show()
    sys.exit(app.exec_())
