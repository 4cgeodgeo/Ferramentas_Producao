import os

from Ferramentas_Producao.controllers.loginCtrl import LoginCtrl
from Ferramentas_Producao.controllers.remoteProdToolsDockCtrl import RemoteProdToolsDockCtrl
from Ferramentas_Producao.controllers.localProdToolsDockCtrl import LocalProdToolsDockCtrl
from Ferramentas_Producao.controllers.prodToolsSettingsCtrl import ProdToolsSettingsCtrl

from Ferramentas_Producao.modules.sap.controllers.remoteSapCtrl import RemoteSapCtrl
from Ferramentas_Producao.modules.sap.controllers.localSapCtrl import LocalSapCtrl

from Ferramentas_Producao.modules.qgis.qgisCtrl import QgisCtrl
from Ferramentas_Producao.modules.fme.factories.fmeApiSingleton import FmeApiSingleton
from Ferramentas_Producao.modules.utils.factories.utilsFactory import UtilsFactory
from Ferramentas_Producao.modules.dsgTools.factories.processingQgisFactory import ProcessingQgisFactory
from Ferramentas_Producao.modules.database.factories.databaseFactory import DatabaseFactory
from Ferramentas_Producao.modules.pomodoro.pomodoro import Pomodoro
from Ferramentas_Producao.config import Config

class Main:

    def __init__(self, iface):    
        super(Main, self).__init__()
        self.plugin_dir = os.path.dirname(__file__)
        self.iface = iface
        self.qgisCtrl = QgisCtrl()
        self.prodToolsSettingsCtrl = ProdToolsSettingsCtrl( self.qgisCtrl )
        self.remoteProdToolsDockCtrl = RemoteProdToolsDockCtrl(
            sap=RemoteSapCtrl( self.qgisCtrl ),
            qgis=self.qgisCtrl,
            databaseFactory=DatabaseFactory(),
            processingFactory=ProcessingQgisFactory(),
            fme=FmeApiSingleton.getInstance(),
            pomodoro=Pomodoro(self.iface),
            prodToolsSettings=self.prodToolsSettingsCtrl
        )
        self.localProdToolsDockCtrl = LocalProdToolsDockCtrl(
            sap=LocalSapCtrl( self.qgisCtrl ),
            qgis=self.qgisCtrl,
            databaseFactory=DatabaseFactory(),
            processingFactory=ProcessingQgisFactory(),
            prodToolsSettings=self.prodToolsSettingsCtrl
        )
        self.loginCtrl = LoginCtrl(
            qgis=self.qgisCtrl,
            remoteProdToolsDockCtrl=self.remoteProdToolsDockCtrl,
            localProdToolsDockCtrl=self.localProdToolsDockCtrl
        )
        self.externalInstances = []
    
    def getPluginIconPath(self):
        return os.path.join(
            os.path.abspath(os.path.join(
                os.path.dirname(__file__)
            )),
            'icons',
            'production.png'
        )

    def initGui(self):
        self.action = self.qgisCtrl.createAction(
            Config.NAME,
            self.getPluginIconPath(),
            self.startPlugin   
        )
        self.qgisCtrl.addActionDigitizeToolBar(self.action)
        self.qgisCtrl.loadProcessingProvider(self.getPluginIconPath())
        self.prodToolsSettingsCtrl.load()
        
    def unload(self):
        self.qgisCtrl.removeActionDigitizeToolBar(self.action)
        self.qgisCtrl.unloadProcessingProvider()
        self.remoteProdToolsDockCtrl.unload()
        self.localProdToolsDockCtrl.unload()
        self.prodToolsSettingsCtrl.unload()
        
    def startPlugin(self, b):
        self.loginCtrl.showView()

    def startPluginExternally(self, remoteSapCtrl):
        remoteProdToolsDockCtrl = RemoteProdToolsDockCtrl(
            sap=remoteSapCtrl,
            qgis=self.qgisCtrl,
            databaseFactory=DatabaseFactory(),
            processingFactory=ProcessingQgisFactory(),
            fme=FmeApiSingleton.getInstance(),
            pomodoro=Pomodoro(self.iface),
            prodToolsSettings=self.prodToolsSettingsCtrl
        )
        remoteProdToolsDockCtrl.loadDockWidget()
        self.externalInstances.append(remoteProdToolsDockCtrl)