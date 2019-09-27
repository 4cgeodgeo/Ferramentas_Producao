# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtWidgets
from .loginAction import LoginAction
from .loginDialog import LoginDialog
import sys, os
from Ferramentas_Producao.utils import msgBox, cursorWait
from Ferramentas_Producao.utils.managerQgis import ManagerQgis

class Login(QtCore.QObject):

    sap = QtCore.pyqtSignal(str, str, str)
    local = QtCore.pyqtSignal(bool)

    def __init__(self, iface):
        super(Login, self).__init__()
        self.iface = iface
        self.action = LoginAction(self.iface)
        self.action.show_login_dialog.connect(
            self.show_login_dialog
        )
        self.dialog = LoginDialog(self.iface)
        self.dialog.login_local.connect(
            self.login_local
        )
        self.dialog.login_remote.connect(
            self.login_remote
        )

    def login_local(self, login_data):
        self.dialog.accept()
        self.local.emit(False)
       
    def login_remote(self, login_data):
        server = login_data['server']
        user = login_data['user']
        password = login_data['password']
        m_qgis = ManagerQgis(self.iface)
        m_qgis.save_qsettings_var('login/server', server)
        m_qgis.save_project_var('user', user)
        m_qgis.save_project_var('password', password)
        self.sap.emit(server, user, password)

    def show_login_dialog(self):
        m_qgis = ManagerQgis(self.iface)
        server = m_qgis.load_qsettings_var('login/server')
        user = m_qgis.load_project_var('user')
        password = m_qgis.load_project_var('password')
        self.dialog.load_login_data(server, user, password)
        self.dialog.show_()
        