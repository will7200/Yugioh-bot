#!/usr/bin/env python


#############################################################################
##
# Copyright (C) 2013 Riverbank Computing Limited.
# Copyright (C) 2010 Nokia Corporation and/or its subsidiary(-ies).
# All rights reserved.
##
# This file is part of the examples of PyQt.
##
# $QT_BEGIN_LICENSE:BSD$
# You may use this file under the terms of the BSD license as follows:
##
# "Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
# * Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in
# the documentation and/or other materials provided with the
# distribution.
# * Neither the name of Nokia Corporation and its Subsidiary(-ies) nor
# the names of its contributors may be used to endorse or promote
# products derived from this software without specific prior written
# permission.
##
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
# $QT_END_LICENSE$
##
#############################################################################
import time

from PyQt5 import QtCore
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QAction, QApplication, QCheckBox, QComboBox,
                             QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
                             QMessageBox, QMenu, QPushButton, QSpinBox, QStyle, QSystemTrayIcon,
                             QTextEdit, QVBoxLayout, QDesktopWidget, QWidget, QFrame)
from enum import Enum
from bot.duel_links_runtime import DuelLinkRunTime
from bot import images_qr


class WINDOWS_TASKBAR_LOCATION(Enum):
    LEFT = 1
    TOP = 2
    RIGHT = 3
    BOTTOM = 4


app_name = "Yugioh-DuelLinks Bot"
default_open_offset = 7


def mock_data(): return False


update_intervals = {
    'next_run_at': 10,
    'nox_status': 10,
    'current_time': 1
}


class DuelLinksGui(QFrame):
    _shouldShowSystrayBox = mock_data
    dlRunTime = None

    def __init__(self, duelLinksRunTime=None, assets=None):
        super(DuelLinksGui, self).__init__()
        self.assets = assets
        # if duelLinksRunTime is None:
        #    raise Exception("Duel Links Run Time Invalid")
        self.dlRunTime = duelLinksRunTime  # type: DuelLinkRunTime
        #self.createIconGroupBox()
        self.createRunTimeFields()
        self.createMessageGroupBox()
        self.createBotControls()

        # self.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)
        # self.setLineWidth(2)
        self.setObjectName("BotFrame")
        self.setStyleSheet("#BotFrame {border: 2px solid #9e3939;}")
        # self.iconLabel.setMinimumWidth(self.durationLabel.sizeHint().width())

        self.createActions()
        self.createBotActions()
        self.createTrayIcon()
        self.setShouldShowSystrayBox(mock_data)
        # self.showMessageButton.clicked.connect(self.showMessage)
        self.hideButton.clicked.connect(self.close)
        self.exitButton.clicked.connect(self.__quit__)
        # self.showIconCheckBox.toggled.connect(self.trayIcon.setVisible)
        # self.iconComboBox.currentIndexChanged.connect(self.setIcon)
        self.trayIcon.messageClicked.connect(self.messageClicked)
        self.trayIcon.activated.connect(self.iconActivated)

        # bot actions connected

        self.pauseButton.clicked.connect(self.pause_bot)
        self.runButton.clicked.connect(self.start_bot)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.runTimeGroupBox)
        mainLayout.addWidget(self.botControls)
        # mainLayout.addWidget(self.iconGroupBox)
        # mainLayout.addWidget(self.messageGroupBox)
        self.setLayout(mainLayout)

        self.setIcon(0)
        self.trayIcon.show()
        self.setWindowTitle(app_name)
        self.setFixedSize(400, 300)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Popup)
        self.location_on_the_screen()
        self.update_values(True)

    def location_on_the_screen(self):
        ag = QDesktopWidget().availableGeometry()
        sg = QDesktopWidget().screenGeometry()

        widget = self.geometry()
        position = self.get_task_bar_position()
        if position == WINDOWS_TASKBAR_LOCATION.BOTTOM:
            x = ag.width() - widget.width()
            y = 2 * ag.height() - sg.height() - widget.height()
        elif position == WINDOWS_TASKBAR_LOCATION.LEFT:
            x = sg.width() - ag.width() + default_open_offset
            y = 2 * ag.height() - sg.height() - widget.height() - default_open_offset
        self.move(x, y)

    def get_task_bar_position(self):
        desktop = QDesktopWidget()
        displayRect = desktop.screenGeometry()
        desktopRect = desktop.availableGeometry()
        if desktopRect.height() < displayRect.height():
            if desktopRect.y() > displayRect.y():
                return WINDOWS_TASKBAR_LOCATION.TOP
            else:
                return WINDOWS_TASKBAR_LOCATION.BOTTOM
        else:
            if desktopRect.x() > displayRect.x():
                return WINDOWS_TASKBAR_LOCATION.LEFT
            else:
                return WINDOWS_TASKBAR_LOCATION.RIGHT

    def setVisible(self, visible):
        self.minimizeAction.setEnabled(visible)
        self.maximizeAction.setEnabled(not self.isMaximized())
        self.restoreAction.setEnabled(self.isMaximized() or not visible)
        super(DuelLinksGui, self).setVisible(visible)

    def closeEvent(self, event):
        if self.trayIcon.isVisible():
            if self.shouldShowSystrayBox():
                QMessageBox.information(self, app_name,
                                        "The program will keep running in the system tray. To "
                                        "terminate the program, choose <b>Quit</b> in the "
                                        "context menu of the system tray entry.")
            self.hide()
            event.ignore()

    def setShouldShowSystrayBox(self, callback):
        self._shouldShowSystrayBox = callback

    def shouldShowSystrayBox(self):
        self._shouldShowSystrayBox()

    def setIcon(self, index):
        icon = QIcon(QIcon(':/assets/yugioh.ico'))
        self.trayIcon.setIcon(icon)
        self.setWindowIcon(icon)

        self.trayIcon.setToolTip('Duel-Links Bot')

    def iconActivated(self, reason):
        if reason in (QSystemTrayIcon.Trigger, QSystemTrayIcon.DoubleClick):
            self.showNormal()
        elif reason == QSystemTrayIcon.MiddleClick:
            self.showNotifcation(
                "In Development", "You pressed the middle mouse button.\n Hidden Feature!!!!")

    def showMessage(self):
        icon = QSystemTrayIcon.MessageIcon(
            self.typeComboBox.itemData(self.typeComboBox.currentIndex()))
        self.trayIcon.showMessage(self.titleEdit.text(),
                                  self.bodyEdit.toPlainText(), icon,
                                  self.durationSpinBox.value() * 1000)

    def showNotifcation(self, title, message):
        icon = QSystemTrayIcon.MessageIcon(
            self.typeComboBox.itemData(self.typeComboBox.currentIndex()))
        self.trayIcon.showMessage(title,
                                  message, icon,
                                  self.durationSpinBox.value() * 1000)

    def messageClicked(self):
        QMessageBox.information(None, "Systray",
                                "Sorry, I already gave what help I could.\nMaybe you should "
                                "try asking a human?")

    def createIconGroupBox(self):
        self.iconGroupBox = QGroupBox("Tray Icon")

        self.iconLabel = QLabel("Icon:")

        self.iconComboBox = QComboBox()
        self.iconComboBox.addItem(QIcon('assets/yugioh.ico'), "Duel-Card")

        self.showIconCheckBox = QCheckBox("Show icon")
        self.showIconCheckBox.setChecked(True)

        iconLayout = QHBoxLayout()
        iconLayout.addWidget(self.iconLabel)
        iconLayout.addWidget(self.iconComboBox)
        iconLayout.addStretch()
        iconLayout.addWidget(self.showIconCheckBox)
        self.iconGroupBox.setLayout(iconLayout)

    def createBotControls(self):
        self.botControls = QGroupBox("Controls")
        controlLayout = QGridLayout()
        runLabel = QLabel("Run the bot:")
        self.runButton = QPushButton("Run")
        showLabel = QLabel("Pause the bot:")
        self.pauseButton = QPushButton("Pause")
        self.exitButton = QPushButton("Exit")
        self.hideButton = QPushButton("Hide")
        controlLayout.addWidget(runLabel, 0, 0)
        controlLayout.addWidget(self.runButton, 0, 2, 1, 2)
        controlLayout.addWidget(showLabel, 1, 0)
        controlLayout.addWidget(self.pauseButton, 1, 2, 1, 2)
        controlLayout.addWidget(self.hideButton, 2, 0, 1, 2)
        controlLayout.addWidget(self.exitButton, 2, 2, 1, 2)
        self.botControls.setLayout(controlLayout)

    def createMessageGroupBox(self):
        # self.messageGroupBox = QGroupBox("Balloon Message")

        typeLabel = QLabel("Type:")

        self.typeComboBox = QComboBox()
        self.typeComboBox.addItem("None", QSystemTrayIcon.NoIcon)
        self.typeComboBox.addItem(self.style().standardIcon(
            QStyle.SP_MessageBoxInformation), "Information",
            QSystemTrayIcon.Information)
        self.typeComboBox.addItem(self.style().standardIcon(
            QStyle.SP_MessageBoxWarning), "Warning",
            QSystemTrayIcon.Warning)
        self.typeComboBox.addItem(self.style().standardIcon(
            QStyle.SP_MessageBoxCritical), "Critical",
            QSystemTrayIcon.Critical)
        self.typeComboBox.setCurrentIndex(1)

        self.durationLabel = QLabel("Duration:")

        self.durationSpinBox = QSpinBox()
        self.durationSpinBox.setRange(5, 60)
        self.durationSpinBox.setSuffix(" s")
        self.durationSpinBox.setValue(15)

        durationWarningLabel = QLabel("(some systems might ignore this hint)")
        durationWarningLabel.setIndent(10)

        titleLabel = QLabel("Title:")

        self.titleEdit = QLineEdit("Cannot connect to network")

        bodyLabel = QLabel("Body:")

        self.bodyEdit = QTextEdit()
        self.bodyEdit.setPlainText("Don't believe me. Honestly, I don't have "
                                   "a clue.\nClick this balloon for details.")

        # self.showMessageButton = QPushButton("Show Message")
        # self.showMessageButton.setDefault(True)
        """
        messageLayout = QGridLayout()
        messageLayout.addWidget(typeLabel, 0, 0)
        messageLayout.addWidget(self.typeComboBox, 0, 1, 1, 2)
        messageLayout.addWidget(self.durationLabel, 1, 0)
        messageLayout.addWidget(self.durationSpinBox, 1, 1)
        messageLayout.addWidget(durationWarningLabel, 1, 2, 1, 3)
        messageLayout.addWidget(titleLabel, 2, 0)
        messageLayout.addWidget(self.titleEdit, 2, 1, 1, 4)
        messageLayout.addWidget(bodyLabel, 3, 0)
        messageLayout.addWidget(self.bodyEdit, 3, 1, 2, 4)
        messageLayout.addWidget(self.showMessageButton, 5, 4)
        messageLayout.setColumnStretch(3, 1)
        messageLayout.setRowStretch(4, 1)
        self.messageGroupBox.setLayout(messageLayout)"""

    def createRunTimeFields(self):
        self.runTimeGroupBox = QGroupBox("RunTime Fields")
        self.current_time = QLabel("Current Time: ")
        self.current_time_value = QLabel("")
        self.nox_status_label = QLabel("{} status: ".format(self.dlRunTime.get_provider().__str__()))
        self.nox_status_value = QLabel("")
        self.next_run_at_label = QLabel("Next Run At:")
        self.next_run_at_value = QLabel("")
        self.in_timer = QtCore.QTimer(self)
        self.in_timer.setInterval(1000)
        self.in_timer.timeout.connect(self.update_values)
        self.in_timer.start()
        layout = QVBoxLayout()
        top = QHBoxLayout()
        top.addWidget(self.current_time)
        top.addWidget(self.current_time_value)
        top.addStretch()
        runTimeLayout = QHBoxLayout()
        runTimeLayout.addWidget(self.nox_status_label)
        runTimeLayout.addWidget(self.nox_status_value)
        runTimeLayout.addStretch()
        runTimeLayout.addWidget(self.next_run_at_label)
        runTimeLayout.addWidget(self.next_run_at_value)
        layout.addLayout(top)
        layout.addLayout(runTimeLayout)
        self.runTimeGroupBox.setLayout(layout)

    _counter = 0

    def update_values(self, force=False):
        self._counter += 1
        if self._counter % update_intervals.get('current_time', 1) == 0 or force:
            self.current_time_value.setText(QtCore.QDateTime.currentDateTime().toString())
        if self._counter % update_intervals.get('nox_status', 1) == 0 or force:
            self.nox_status_value.setText(
                (lambda: "Running" if self.dlRunTime.get_provider().is_process_running() else "Off")())
        if self._counter % update_intervals.get('next_run_at', 1) == 0 or force:
            self.next_run_at_value.setText(self.dlRunTime.next_run_at.strftime("%Y-%m-%dT%H:%M:%S"))
        if self.dlRunTime.get_provider().current_thread is not None:
            self.runButton.setDisabled(False)
            self.runButton.setEnabled(False)
            self.pauseButton.setDisabled(True)
            self.pauseButton.setEnabled(True)
        else:
            self.runButton.setDisabled(True)
            self.runButton.setEnabled(True)
            self.pauseButton.setDisabled(False)
            self.pauseButton.setEnabled(False)
        if self.dlRunTime._shutdown:
            self.hide()
            QApplication.instance().quit()

    def createActions(self):
        self.minimizeAction = QAction("Mi&nimize", self, triggered=self.hide)
        self.maximizeAction = QAction("Ma&ximize", self,
                                      triggered=self.showMaximized)
        self.restoreAction = QAction("&Restore", self,
                                     triggered=self.showNormal)
        self.quitAction = QAction("&Quit", self,
                                  triggered=self.__quit__)

    def __quit__(self):
        self.hide()
        self.dlRunTime.shutdown()
        QApplication.instance().quit()

    def createBotActions(self):
        self.startAction = QAction('Start', self, triggered=self.start_bot)
        self.pauseAction = QAction('Pause', self, triggered=self.pause_bot)

    def start_bot(self):
        self.dlRunTime.stop = False
        self.dlRunTime.run_now = True

    def pause_bot(self):
        self.dlRunTime.stop = True
        self.dlRunTime.run_now = False

    def createTrayIcon(self):
        self.trayIconMenu = QMenu(self)
        self.trayIconMenu.addAction(self.minimizeAction)
        self.trayIconMenu.addAction(self.maximizeAction)
        self.trayIconMenu.addAction(self.restoreAction)
        self.trayIconMenu.addSeparator()
        self.trayIconMenu.addAction(self.quitAction)

        self.trayIcon = QSystemTrayIcon(self)
        self.trayIcon.setContextMenu(self.trayIconMenu)


if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)

    if not QSystemTrayIcon.isSystemTrayAvailable():
        QMessageBox.critical(None, "Systray",
                             "Systray not dected on system.")
        sys.exit(1)

    QApplication.setQuitOnLastWindowClosed(False)

    window = Window()
    window.show()
    sys.exit(app.exec_())
