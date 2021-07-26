
from Ferramentas_Producao.factories.GUIFactory import GUIFactory
from Ferramentas_Producao.factories.timerFactory import TimerFactory
from Ferramentas_Producao.controllers.prodToolsCtrl import ProdToolsCtrl
from PyQt5 import QtWidgets
from qgis import core, gui, utils

import os

class RemoteProdToolsDockCtrl(ProdToolsCtrl):

    iconRootPath = os.path.join(
            os.path.dirname(__file__),
            '..',
            'icons'
    )
    
    def __init__(
            self,
            sap,
            qgis,
            databaseFactory,
            processingFactory,
            fme,
            pomodoro,
            prodToolsSettings,
            guiFactory=GUIFactory()
        ):
        super(RemoteProdToolsDockCtrl, self).__init__()
        self.sap = sap
        self.qgis = qgis
        self.fme = fme
        self.databaseFactory = databaseFactory
        self.processingFactory = processingFactory
        self.guiFactory = guiFactory
        self.pomodoro = pomodoro
        self.prodToolsSettings = prodToolsSettings
        self.sapActivity = None
        self.productionTools = None
        self.changeStyleWidget = None
        self.qgis.on('ReadProject', self.readProjectCallback)
        self.qgis.on('MessageLog', self.handleMessageLogPostgis)
        self.loadedLayerIds = []

    def closedDock(self):
        #self.changeStyleWidget.clearStyles() if self.changeStyleWidget else ''
        pass
        
    def authUser(self, username, password, server):
        self.qgis.setProjectVariable('productiontools:user', username)
        self.qgis.setProjectVariable('productiontools:password', password)
        self.qgis.setSettingsVariable('productiontools:server', server)
        return self.sap.authUser(username, password, server)

    def getPomodoroWidget(self):
        return self.pomodoro.getWidget() if self.pomodoro else None
        
    def unload(self):
        self.removeDock()
        self.qgis.off('ReadProject', self.readProjectCallback)
        self.qgis.off('MessageLog', self.handleMessageLogPostgis)
        self.pomodoro.unload()

    def reload(self):
        if self.productionTools is None:
            return
        self.sapActivity = self.sap.getActivity()
        if self.sapActivity is None:
            self.removeDock()
            return
        self.loadShortcuts()
        self.productionTools = self.guiFactory.makeRemoteProductionToolsDock(self, self.productionTools)

    def loadShortcuts(self):
        shortcuts = self.sapActivity.getShortcuts()
        for shortcut in shortcuts:
            self.qgis.setActionShortcut(shortcut['ferramenta'], shortcut['atalho'])

    def loadChangeStyleTool(self, stylesName):
        if self.changeStyleWidget and self.changeStyleAction:
            return
        self.changeStyleWidget = self.guiFactory.getWidget('ChangeStyleWidget', controller=self)
        self.changeStyleAction = self.qgis.createAction(
            'Paginar estilo',
            os.path.join(self.iconRootPath, 'changeStyles.png'),
            self.changeStyleWidget.page
        )
        self.changeStyleWidget.loadStyles(stylesName, stylesName[0])
        self.qgis.addWidgetToolBar(self.changeStyleWidget)
        self.qgis.addActionToolBar(self.changeStyleAction)
            
    def changeMapLayerStyle(self, styleName):
        self.qgis.changeMapLayerStyles(styleName)

    def loadDockWidget(self, sapActivity=None):
        self.sapActivity = self.sap.getActivity() if sapActivity is None else sapActivity
        if not self.sapActivity:
            return
        self.loadShortcuts()
        self.loadChangeStyleTool( self.sapActivity.getStylesName() )
        self.productionTools = self.guiFactory.makeRemoteProductionToolsDock(self)
        self.qgis.addDockWidget(self.productionTools, side='left')        

    def removeDock(self):
        self.qgis.removeDockWidget(self.productionTools) if self.productionTools else ''
    
    def getShortcutQgisDescription(self):
        return self.prodToolsSettings.getShortcutQgisDescription()

    def getActivityDescription(self):
        return self.sapActivity.getDescription()

    def getActivityLineage(self):
        return self.sapActivity.getLineage()

    def getActivityNotes(self):
        return self.sapActivity.getNotes()

    def getActivityRequirements(self):
        return self.sapActivity.getRequirements()

    def getActivityEPSG(self):
        return self.sapActivity.getEPSG()

    def getUserName(self):
        return self.sapActivity.getUserName()

    def getActivityStyles(self):
        return self.sapActivity.getStylesName()

    def showEndActivityDialog(self):
        if self.qgis.hasModifiedLayers():
            self.showInfoMessageBox(
                self.productionTools,
                'Aviso',
                'Salve todas suas alterações antes de finalizar!'
            )
            return
        result = self.sap.showEndActivityDialog()
        if not result:
            return
        self.reload()
        self.qgis.cleanProject()

    def showReportErrorDialog(self):
        result = self.sap.showReportErrorDialog()
        if not result:
            return
        self.reload()
        self.qgis.cleanProject()

    def getActivityDatabase(self):
        return self.databaseFactory.createPostgres(
            self.sapActivity.getDatabaseName(), 
            self.sapActivity.getDatabaseServer(), 
            self.sapActivity.getDatabasePort(), 
            self.sapActivity.getDatabaseUserName(), 
            self.sapActivity.getDatabasePassword()
        )

    def getActivityLayerNames(self):
        return [item["nome"] for item in self.sapActivity.getLayers()]

    def getActivityInputs(self):
        return self.sapActivity.getInputs()

    def loadActivityLayers(self, onlyWithFeatures):
        loadLayersFromPostgis = self.processingFactory.createProcessing('LoadLayersFromPostgis', self)
        result = loadLayersFromPostgis.run({ 
            'dbName' : self.sapActivity.getDatabaseName(), 
            'dbHost' : self.sapActivity.getDatabaseServer(), 
            'layerNames' : self.getActivityLayerNames(), 
            'dbPassword' : self.sapActivity.getDatabasePassword(), 
            'dbPort' : self.sapActivity.getDatabasePort(), 
            'dbUser' : self.sapActivity.getDatabaseUserName() 
        })
        loadedLayerIds = result['OUTPUT']

        if not( self.sapActivity.getTypeProductionData() == 2 ):
            assingFilterToLayers = self.processingFactory.createProcessing('AssingFilterToLayers', self)
            assingFilterToLayers.run({'layers': self.sapActivity.getLayers()})
    
        if onlyWithFeatures:
            self.qgis.removeLayersWithouFeatures(loadedLayerIds)

        groupLayers = self.processingFactory.createProcessing('GroupLayers', self)
        groupLayers.run({'layerIds': loadedLayerIds})

        defaultStyle = self.getActivityStyles()[0]
        self.qgis.loadMapLayerStyles(
            loadedLayerIds,
            self.sapActivity.getLayerStyles(),
            defaultStyle
        )
        self.changeStyleWidget.loadStyles(self.getActivityStyles(), defaultStyle)

        """ matchAndApplyQmlStylesToLayers = self.processingFactory.createProcessing('MatchAndApplyQmlStylesToLayers', self)
        matchAndApplyQmlStylesToLayers.run({
            'layersQml': self.sapActivity.getLayersQml(styleName),
            'layerIds': loadedLayerIds
        }) """

        assignValueMapToLayers = self.processingFactory.createProcessing('AssignValueMapToLayers', self)
        database = self.getActivityDatabase()
        assignValueMapToLayers.run({
            'valueMaps': {
                    layer["nome"]: database.getAttributeValueMap(layer["nome"], layer["schema"])
                    for layer in self.sapActivity.getLayers()
            },
            'layerIds': loadedLayerIds
        }) 

        assignMeasureColumnToLayers = self.processingFactory.createProcessing('AssignMeasureColumnToLayers', self)
        assignMeasureColumnToLayers.run({'layerIds': loadedLayerIds})

        assignAliasesToLayers = self.processingFactory.createProcessing('AssignAliasesToLayers', self)
        assignAliasesToLayers.run({
            'aliases': self.sapActivity.getLayerALiases(),
            'layerIds': loadedLayerIds
        })

        assignActionsToLayers = self.processingFactory.createProcessing('AssignActionsToLayers', self)
        assignActionsToLayers.run({
            'actions': self.sapActivity.getLayerActions(),
            'layerIds': loadedLayerIds
        })

        assignDefaultFieldValueToLayers = self.processingFactory.createProcessing('AssignDefaultFieldValueToLayers', self)
        assignDefaultFieldValueToLayers.run({
            'defaultValues': self.sapActivity.getLayerDefaultFieldValue(),
            'layerIds': loadedLayerIds
        })

        assignExpressionFieldToLayers = self.processingFactory.createProcessing('AssignExpressionFieldToLayers', self)
        assignExpressionFieldToLayers.run({
            'expressions': self.sapActivity.getLayerExpressionField(),
            'layerIds': loadedLayerIds
        })

        assignConditionalStyleToLayers = self.processingFactory.createProcessing('AssignConditionalStyleToLayers', self)
        assignConditionalStyleToLayers.run({
            'conditionals': self.sapActivity.getLayerConditionalStyle(),
            'layerIds': loadedLayerIds
        })

        self.qgis.loadInputData({
            'query': self.sapActivity.getFrameQuery(),
            'epsg': self.sapActivity.getEPSG(),
            'nome': 'moldura',
            'tipo_insumo_id': 100,
            'qml': self.sapActivity.getFrameQml()
        })
        self.qgis.loadDefaultFieldValue(loadedLayerIds)
        self.qgis.loadLayerActions(loadedLayerIds)
        
        self.prodToolsSettings.initSaveTimer()

    def setLoadedLayerIds(self, loadedLayerIds):
        self.loadedLayerIds = loadedLayerIds

    def getLoadedLayerIds(self):
        return self.loadedLayerIds

    def getPathDest(self):
        return QtWidgets.QFileDialog.getExistingDirectory(
            self.productionTools if self.productionTools else utils.iface.mainWindow(), 
            u"Selecione pasta de destino dos insumos:",
            options=QtWidgets.QFileDialog.ShowDirsOnly
        )

    def loadActivityInputs(self, inputData):
        results = []
        if not inputData:
            self.showInfoMessageBox(None, 'Aviso', 'Selecione o(s) insumo(s)!')
            return
        for data in inputData:
            if data['tipo_insumo_id'] in [1]:
                pathDest = self.getPathDest()
                if not pathDest:
                    continue
                data['caminho_padrao'] = pathDest
            result = self.qgis.loadInputData(data)
            results.append(result)
        return results

    def getActivityRoutines(self):
        fmeData = []
        #try:
        fmeData = self.fme.getSapRoutines(self.sapActivity.getFmeConfig())
        #except Exception as e:
        #    self.showErrorMessageBox(None, 'Erro', 'Sem conexão com o FME!')
        return self.sapActivity.getQgisModels() + self.sapActivity.getRuleRoutines() + fmeData

    def runRoutine(self, routineData):
        if not routineData:
            self.showInfoMessageBox(None, 'Aviso', 'Selecione uma rotina!')
            return
        if self.qgis.hasModifiedLayers():
            self.showHtmlMessageDialog(
                self.qgis.getMainWindow(),
                'Aviso',
                '''<p style="color:red">
                    Salve todas suas alterações antes de executar essa rotina!
                </p>'''
            )
            return
        rountineFunctions = {
            'rules': self.runRuleStatistics,
            'fme': self.runFMESAP,
            'qgisModel': self.runQgisModel
        }
        html = rountineFunctions[routineData['routineType']](routineData)
        self.showHtmlMessageDialog(
            self.qgis.getMainWindow(),
            'Aviso',
            html
        )
        #self.qgis.setSettingsVariable('productiontools:user', user)
        #self.qgis.getSettingsVariable('productiontools:user')

    def runFMESAP(self, routineData):
        runFMESAP = self.processingFactory.createProcessing('RunFMESAP', self)
        output = runFMESAP.run({
            'workUnitGeometry': self.sapActivity.getWorkUnitGeometry(),
            'fmeRoutine': routineData,
            'dbName': self.sapActivity.getDatabaseName(),
            'dbPort': self.sapActivity.getDatabasePort(),
            'dbHost': self.sapActivity.getDatabaseServer()
        })
        summary = output['result']['dados']['sumario']
        html = "<p>[rotina nome] : {0}</p>".format(routineData['rotina'])
        html += "<p>[status de execução] : {0}</p>".format(output['result']['dados']['status'])
        for flags in output['result']['dados']['sumario']:
            html += """<p>[rotina flags] : {} - {}</p>""".format(flags['classes'], flags['feicoes'])
        return html

    def runRuleStatistics(self, routineData):
        ruleStatistics = self.processingFactory.createProcessing('RuleStatistics', self)
        return ruleStatistics.run({
            'rules': routineData['ruleStatistics'],
            'layers': self.sapActivity.getLayers()
        })

    def runQgisModel(self, routineData):
        return self.qgis.runProcessingModel(routineData)

    def showActivityDataSummary(self):
        dialog = self.guiFactory.makeActivitySummaryDialog(
            self,
            self.getActivityLayerNames(),
            self.sapActivity.getConditionalStyleNames()
        )
        dialog.exec_()

    def showHtmlMessageDialog(self, parent, title, message):
        htmlMessageDlg = self.messageFactory.createMessage('HtmlMessageDialog')
        htmlMessageDlg.show(parent, title, message)

    def showInfoMessageBox(self, parent, title, message):
        messageDlg = self.messageFactory.createMessage('InfoMessageBox')
        messageDlg.show(parent, title, message)
    
    def showErrorMessageBox(self, parent, title, message):
        messageDlg = self.messageFactory.createMessage('ErrorMessageBox')
        messageDlg.show(parent, title, message)

    def readProjectCallback(self):
        self.productionTools.close() if self.productionTools else ''
        if self.sap.isValidActivity():
            self.prodToolsSettings.initSaveTimer()
            return
        self.qgis.cleanProject()
        self.showInfoMessageBox(
            self.qgis.getMainWindow(),
            'Aviso',
            '''
            <p style="color:red">
                Esse projeto não pode ser acessado. Carregue um novo projeto.
            </p>
            '''
        )

    def handleMessageLogPostgis(self, *args):
        if not( args[1].lower() == 'postgis'):
            return
        text = args[0]
        if not 'feição desatualizada:' in text.lower():
            return
        layerName, layerId = text.lower().split('feição desatualizada:')[-1].split('-')
        errorWidget = self.productionTools.getErrorWidget()
        errorWidget.addRow(layerId, layerName, 'feição desatualizada')
        errorWidget.adjustColumns() 
        self.showErrorMessageBox(None, 'Erro', 'Algumas feições não foram modificadas!')
        self.productionTools.setBadgeTabErrorsEnabled(True)    

    def zoomToFeature(self, layerId, layerSchema, layerName):
        self.qgis.zoomToFeature(layerId, layerSchema, layerName)  
