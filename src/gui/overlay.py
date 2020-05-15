# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'overlay.ui'
#
# Created by: PyQt5 UI code generator 5.12.3
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class DragButton(QtWidgets.QPushButton):

    def mousePressEvent(self, event):
        self.__mousePressPos = None
        self.__mouseMovePos = None
        
        if event.button() == QtCore.Qt.LeftButton:
            self.__mousePressPos = event.globalPos()
            self.__mouseMovePos = event.globalPos()

        super(DragButton, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() == QtCore.Qt.LeftButton:
            # adjust offset from clicked point to origin of widget
            currPos = self.mapToGlobal(self.pos())
            globalPos = event.globalPos()
            diff = globalPos - self.__mouseMovePos
            newPos = self.mapFromGlobal(currPos + diff)
            
            self.move(newPos)

            self.__mouseMovePos = globalPos

        super(DragButton, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.__mousePressPos is not None:
            moved = event.globalPos() - self.__mousePressPos 
            
            if moved.manhattanLength() > 3:
                event.ignore()
                return

        super(DragButton, self).mouseReleaseEvent(event)


class DragTable(QtWidgets.QTableWidget):

    def mousePressEvent(self, event):
        self.__mousePressPos = None
        self.__mouseMovePos = None
        
        if event.button() == QtCore.Qt.LeftButton:
            self.__mousePressPos = event.globalPos()
            self.__mouseMovePos = event.globalPos()

        super(DragTable, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() == QtCore.Qt.LeftButton:
            # adjust offset from clicked point to origin of widget
            currPos = self.mapToGlobal(self.pos())
            globalPos = event.globalPos()
            diff = globalPos - self.__mouseMovePos
            newPos = self.mapFromGlobal(currPos + diff)
            
            self.move(newPos)

            self.__mouseMovePos = globalPos

        super(DragTable, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.__mousePressPos is not None:
            moved = event.globalPos() - self.__mousePressPos 
            
            if moved.manhattanLength() > 3:
                event.ignore()
                return

        super(DragTable, self).mouseReleaseEvent(event)


class Ui_Overlay(object):
    def setupUi(self, Overlay):
        Overlay.setObjectName("Overlay")
        Overlay.resize(5000, 5000)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Overlay.sizePolicy().hasHeightForWidth())
        Overlay.setSizePolicy(sizePolicy)
        Overlay.setMinimumSize(QtCore.QSize(5000, 5000))
        Overlay.setWindowOpacity(0.5)
        Overlay.setAutoFillBackground(False)
        self.centralwidget = QtWidgets.QWidget(Overlay)
        self.centralwidget.setObjectName("centralwidget")
        self.telem_table = DragTable(self.centralwidget)
        self.telem_table.setGeometry(QtCore.QRect(0, 0, 411, 431))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.telem_table.sizePolicy().hasHeightForWidth())
        self.telem_table.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setFamily("Source Code Pro Semibold")
        font.setPointSize(20)
        font.setBold(True)
        font.setWeight(75)
        self.telem_table.setFont(font)
        self.telem_table.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.telem_table.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.telem_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.telem_table.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.telem_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectItems)
        self.telem_table.setTextElideMode(QtCore.Qt.ElideMiddle)
        self.telem_table.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.telem_table.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.telem_table.setShowGrid(False)
        self.telem_table.setObjectName("telem_table")
        self.telem_table.setColumnCount(0)
        self.telem_table.setRowCount(0)
        self.telem_table.horizontalHeader().setVisible(False)
        self.telem_table.horizontalHeader().setCascadingSectionResizes(True)
        self.telem_table.horizontalHeader().setSortIndicatorShown(False)
        self.telem_table.horizontalHeader().setStretchLastSection(True)
        self.telem_table.verticalHeader().setVisible(False)
        self.telem_table.verticalHeader().setCascadingSectionResizes(True)
        self.telem_table.verticalHeader().setSortIndicatorShown(False)
        self.telem_table.verticalHeader().setStretchLastSection(False)
        self.close_button = DragButton(self.centralwidget)
        self.close_button.setGeometry(QtCore.QRect(0, 440, 231, 23))
        self.close_button.setObjectName("close_button")
        self.field_select_table = DragTable(self.centralwidget)
        self.field_select_table.setGeometry(QtCore.QRect(0, 470, 231, 171))
        self.field_select_table.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.field_select_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.field_select_table.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.field_select_table.setShowGrid(False)
        self.field_select_table.setObjectName("field_select_table")
        self.field_select_table.setColumnCount(0)
        self.field_select_table.setRowCount(0)
        self.field_select_table.horizontalHeader().setVisible(False)
        self.field_select_table.horizontalHeader().setHighlightSections(False)
        self.field_select_table.horizontalHeader().setStretchLastSection(True)
        self.field_select_table.verticalHeader().setVisible(False)
        self.field_select_table.verticalHeader().setHighlightSections(False)
        Overlay.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(Overlay)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 5000, 21))
        self.menubar.setObjectName("menubar")
        Overlay.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(Overlay)
        self.statusbar.setObjectName("statusbar")
        Overlay.setStatusBar(self.statusbar)

        self.retranslateUi(Overlay)
        QtCore.QMetaObject.connectSlotsByName(Overlay)

    def retranslateUi(self, Overlay):
        _translate = QtCore.QCoreApplication.translate
        Overlay.setWindowTitle(_translate("Overlay", "Thunder Viewer Overlay"))
        self.telem_table.setSortingEnabled(False)
        self.close_button.setText(_translate("Overlay", "Close Overlay"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Overlay = QtWidgets.QMainWindow()
    ui = Ui_Overlay()
    ui.setupUi(Overlay)
    Overlay.show()
    sys.exit(app.exec_())
