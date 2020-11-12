from Ferramentas_Producao.modules.sap.controllers.sapCtrl import SapCtrl
from Ferramentas_Producao.modules.sap.factories.sapApiHttpSingleton import SapApiHttpSingleton
from Ferramentas_Producao.modules.sap.factories.dataModelFactory import DataModelFactory
from Ferramentas_Producao.modules.sap.factories.guiFactory import GUIFactory
from Ferramentas_Producao.modules.utils.factories.utilsFactory import UtilsFactory

class RemoteSapCtrl(SapCtrl):
    
    def __init__(self, 
            qgis,
            messageFactory=UtilsFactory().createMessageFactory(),
            sapApi=SapApiHttpSingleton.getInstance(),
            dataModelFactory=DataModelFactory(),
            guiFactory=GUIFactory()
        ):
        super(RemoteSapCtrl, self).__init__()
        self.qgis = qgis
        self.messageFactory = messageFactory
        self.dataModelFactory = dataModelFactory
        self.sapApi = sapApi
        self.guiFactory = guiFactory
        self.activityDataModel = self.dataModelFactory.createDataModel('SapActivityHttp')

    def authUser(self, user, password, server):
        self.sapApi.setServer(server)
        response = self.sapApi.loginUser(
            user, 
            password,
            self.qgis.getVersion(),
            self.qgis.getPluginsVersions()
        )
        return response['success']
        
    def getCurrentActivity(self):
        response = self.sapApi.getActivity()
        if not( 'dados' in response and response['dados'] ):
            self.showErrorMessageBox(
                self.qgis.getMainWindow(),
                'Aviso',
                response['message']
            )
            return None
        response['usuario'] = self.qgis.getProjectVariable('productiontools:user')
        response['senha'] = self.qgis.getProjectVariable('productiontools:password')
        return response

    def initActivity(self):
        if not self.showQuestionMessageBox(
                self.qgis.getMainWindow(),
                'Atenção',
                '<p>Deseja iniciar a próxima atividade?</p>'
            ):
            return None
        response = self.sapApi.initActivity()
        if not( response['success'] and 'dados' in response and response['dados'] ):
            self.showErrorMessageBox(
                self.qgis.getMainWindow(),
                'Aviso',
                response['message']
            )
            return None
        return response

    def getUserName(self):
        return self.activityDataModel.getUserName()

    def getActivity(self):
        response = self.getCurrentActivity()
        if response:   
            self.activityDataModel.setData(response)
            self.qgis.setSettingsVariable(
                'productiontools:activityName', 
                self.activityDataModel.getDescription()
            )
            return self.activityDataModel
        response = self.initActivity()
        if response:
            self.activityDataModel.setData(response)
            return self.activityDataModel
        self.showInfoMessageBox(
            self.qgis.getMainWindow(),
            'Aviso',
            '''<p>Não há nenhum trabalho cadastrado para você.
                </p><p>Procure seu chefe de seção.</p>'''
        )
        return None

    def endActivity(self, activityId, withoutCorrection):
        return self.sapApi.endActivity(activityId, withoutCorrection)

    def getErrorsTypes(self):
        response = self.sapApi.getErrorsTypes()
        if not( 'dados' in response ):
            return []
        return response['dados']
    
    def showReportErrorDialog(self, callback):
        reportErrorDialog = self.guiFactory.createReportErrorDialog(self)
        reportErrorDialog.loadErrorsTypes(
            self.getErrorsTypes()
        )
        reportErrorDialog.exec_()
        callback()

    def showEndActivityDialog(self, callback):
        endActivityDialog = self.guiFactory.createEndActivityDialog(self)
        endActivityDialog.exec_()
        callback()
        
    def reportError(self, errorId, errorDescription):
        return self.sapApi.reportError(errorId, errorDescription)

    def hasActivityRecord(self):
        return (
            self.qgis.getProjectVariable('productiontools:user')
            and
            self.qgis.getSettingsVariable('productiontools:server')
            and
            self.qgis.getProjectVariable('productiontools:password')
            and
            self.qgis.getSettingsVariable('productiontools:activityName')
        )

    def hasValidAuthentication(self):
        return self.authUser(
            self.qgis.getProjectVariable('productiontools:user'),
            self.qgis.getProjectVariable('productiontools:password'),
            self.qgis.getSettingsVariable('productiontools:server')
        )

    def isValidActivity(self):
        if not(self.hasActivityRecord()):
            return True
        if not self.hasValidAuthentication():
            return True
        response = self.getCurrentActivity()
        if not response:
            return True   
        currentActivity = self.dataModelFactory.createDataModel('SapActivity')
        currentActivity.setData(response)
        return self.qgis.getSettingsVariable('productiontools:activityName') == currentActivity.getDescription()