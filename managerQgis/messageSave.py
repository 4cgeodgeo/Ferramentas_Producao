# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui
from qgis import core, gui
from time import sleep
import json
import requests
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__),'../'))
from custom_thread.messageTime import MessageTime

class MessageSave(QtCore.QObject):

    def __init__(self, iface, parent=None):
        super(MessageSave, self).__init__(parent)
        self.iface = iface
        self.isRunning = False

    
         
    def show_message(self):
        for lyr in core.QgsMapLayerRegistry.instance().mapLayers().values():
            test = (
                lyr.type() == core.QgsMapLayer.VectorLayer
                and
                lyr.isModified()
            )
            if test:
                QtGui.QMessageBox.information(
                    self.iface.mainWindow(),
                    u"Aviso!", 
                    u"<p style='color:red'>Salve suas edições! (CTRL+S)</p>"
                )
                return

    def start(self):
        self.worker = MessageTime(10*60)
        self.thread = QtCore.QThread()
        self.worker.moveToThread(self.thread)
        self.worker.finish.connect(self.show_message)
        self.thread.started.connect(
            self.worker.run
        )
        self.thread.start()
        self.isRunning = True
        
