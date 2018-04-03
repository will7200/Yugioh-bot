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
import logging
import sys
import time
from enum import Enum

from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QAction, QApplication, QComboBox,
                             QGridLayout, QGroupBox, QHBoxLayout, QLabel, QMessageBox, QMenu, QPushButton,
                             QSystemTrayIcon,
                             QTextEdit, QVBoxLayout, QDesktopWidget, QWidget, QFrame, qApp, QTabWidget, QMainWindow)

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
    'next_run_at' : 10,
    'nox_status'  : 10,
    'current_time': 1
}


class QtHandler(logging.Handler):
    def __init__(self):
        logging.Handler.__init__(self)

    def emit(self, record):
        record = self.format(record)
        if record:
            XStream.stdout().write('%s\n' % record)


class XStream(QtCore.QObject):
    _stdout = None
    _stderr = None
    messageWritten = QtCore.pyqtSignal(str)

    def flush(self):
        pass

    def fileno(self):
        return -1

    def write(self, msg):
        if not self.signalsBlocked():
            self.messageWritten.emit(msg)

    @staticmethod
    def stdout():
        if (not XStream._stdout):
            XStream._stdout = XStream()
            sys.stdout = XStream._stdout
        return XStream._stdout

    @staticmethod
    def stderr():
        if (not XStream._stderr):
            XStream._stderr = XStream()
            sys.stderr = XStream._stderr
        return XStream._stderr


class DuelLinksGui(QFrame, QMainWindow):
    _shouldShowSystrayBox = mock_data
    dlRunTime = None

    def __init__(self, duelLinksRunTime=None, assets=None):
        super(DuelLinksGui, self).__init__()
        self.assets = assets
        assert (type(duelLinksRunTime) is DuelLinkRunTime)
        self.dlRunTime = duelLinksRunTime  # type: DuelLinkRunTime
        self.createRunTimeFields()
        self.createBotControls()

        self.setObjectName("BotFrame")
        self.setStyleSheet("#BotFrame {border: 2px solid #9e3939;}")

        self.createActions()
        self.createBotActions()
        self.createTrayIcon()
        self.setShouldShowSystrayBox(mock_data)
        self.hideButton.clicked.connect(self.close)
        self.exitButton.clicked.connect(self.__quit__)
        self.trayIcon.messageClicked.connect(self.messageClicked)
        self.trayIcon.activated.connect(self.iconActivated)

        # bot actions connected
        self.pauseButton.clicked.connect(self.pause_bot)
        self.runButton.clicked.connect(self.start_bot)

        # log creation
        textViewLog = QtHandler()
        # You can format what is printed to text box
        textViewLog.setFormatter(
            logging.Formatter('%(asctime)s | %(levelname)s | %(name)s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
        logging.getLogger('bot').addHandler(textViewLog)

        # self.textViewLog.signal.connect(self.add_to_log)
        self.tabs = QTabWidget(self)

        self.tab1 = QWidget(self)
        mainLayout = QVBoxLayout(self.tab1)
        mainLayout.addWidget(self.runTimeGroupBox)
        mainLayout.addWidget(self.botControls)
        self.tab1.setLayout(mainLayout)
        self.tabs.addTab(self.tab1, "General")

        self.clear_log = QPushButton("Clear log")
        self.tab2 = QWidget(self)
        logLayout = QVBoxLayout(self.tab2)
        self.textViewLog = QTextEdit(self.tab2)
        self.textViewLog.setReadOnly(True)
        self.clear_log.clicked.connect(self.textViewLog.clear)
        XStream.stdout().messageWritten.connect(self.add_to_log)
        XStream.stderr().messageWritten.connect(self.add_to_log)
        logLayout.addWidget(self.textViewLog)
        logLayout.addWidget(self.clear_log)
        self.tab2.setLayout(logLayout)
        self.tabs.addTab(self.tab2, "Log")

        viewlayout = QVBoxLayout(self)
        viewlayout.addWidget(self.tabs)
        self.setLayout(viewlayout)

        self.setIcon()
        self.trayIcon.show()
        self.setWindowTitle(app_name)
        self.setFixedSize(400, 300)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Popup)
        self.location_on_the_screen()
        self.update_values(True)

    def add_to_log(self, msg):
        try:
            cursor = self.textViewLog.textCursor()
            src = msg.split('|')
            if len(src) != 4:
                self.textViewLog.append(msg)
            else:
                text = ""
                text += "<span>"
                text += "<b>{}</b>".format(src[0])
                text += "<span style=\"color:blue;\">{}</span>".format(src[1])
                text += src[2]
                text += src[3]
                text += "</span>"
                cursor.insertHtml(text + "<br>")
            self.textViewLog.moveCursor(QtGui.QTextCursor.End)
        except Exception as e:
            print('Error on updating log: ', end='')
            print(e)


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
        elif position == WINDOWS_TASKBAR_LOCATION.TOP:
            x = ag.width() - widget.width() - default_open_offset
            y = sg.height() - ag.height() + default_open_offset
        elif position == WINDOWS_TASKBAR_LOCATION.RIGHT:
            x = ag.width() - widget.width() - default_open_offset
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

    def setIcon(self):
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

    def modeChange(self, index):
        self.dlRunTime.playmode = self.available_modes.currentData()

    def createBotControls(self):
        self.botControls = QGroupBox("Controls")
        controlLayout = QGridLayout()
        self.runLabel = QLabel("Run the bot:")
        self.modeLabel = QLabel("Current Mode:")
        self.available_modes = QComboBox()
        for index, mode in enumerate(self.dlRunTime._available_modes):
            self.available_modes.addItem(mode.title(), mode)
        self.available_modes.setStyleSheet("QComboBox {text-align: center;}")
        self.available_modes.setEditable(True)
        self.available_modes.lineEdit().setReadOnly(True)
        self.available_modes.lineEdit().setAlignment(QtCore.Qt.AlignCenter)
        self.available_modes.setCurrentIndex(self.dlRunTime._available_modes.index(self.dlRunTime.playmode))
        self.available_modes.currentIndexChanged.connect(self.modeChange)
        # self.available_modes.lineEdit().setAlignment(QtCore.Qt.AlignCenter)
        self.runButton = QPushButton("Run")
        self.showLabel = QLabel("Pause the bot:")
        self.pauseButton = QPushButton("Pause")
        self.exitButton = QPushButton("Exit")
        self.hideButton = QPushButton("Hide")
        controlLayout.addWidget(self.modeLabel, 0, 0, 1, 2)
        controlLayout.addWidget(self.available_modes, 0, 2, 1, 2)
        controlLayout.addWidget(self.runLabel, 1, 0)
        controlLayout.addWidget(self.runButton, 1, 2, 1, 2)
        controlLayout.addWidget(self.showLabel, 2, 0)
        controlLayout.addWidget(self.pauseButton, 2, 2, 1, 2)
        controlLayout.addWidget(self.hideButton, 3, 0, 1, 2)
        controlLayout.addWidget(self.exitButton, 3, 2, 1, 2)
        self.botControls.setLayout(controlLayout)

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
            self.__quit__()

    def createActions(self):
        self.minimizeAction = QAction("Mi&nimize", self, triggered=self.hide)
        self.maximizeAction = QAction("Ma&ximize", self,
                                      triggered=self.showMaximized)
        self.restoreAction = QAction("&Restore", self,
                                     triggered=self.showNormal)
        self.quitAction = QAction("&Quit", self,
                                  triggered=self.__quit__)

    def __quit__(self):
        QApplication.instance().closingDown()
        self.hide()
        if not self.dlRunTime._shutdown:
            self.dlRunTime.shutdown()
        self.in_timer.stop()
        self.in_timer.deleteLater()
        self.close()
        qApp.closeAllWindows()
        time.sleep(1)
        del self.dlRunTime
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
