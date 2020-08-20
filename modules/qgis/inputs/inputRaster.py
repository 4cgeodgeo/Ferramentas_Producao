from Ferramentas_Producao.modules.qgis.inputs.inputLayer import InputLayer
from qgis import core, gui, utils
from PyQt5 import QtCore, uic, QtWidgets
import platform

class InputRaster(InputLayer):

    def __init__(self):
        super(InputRaster, self).__init__()

    def loadRaster(self, uri, name, epsg):
        s = QtCore.QSettings()
        defaultBehavior = s.value("Projections/defaultBehavior")
        s.setValue("Projections/defaultBehavior", "useGlobal")
        layer = core.QgsRasterLayer(d['caminho_arquivo'], d['nome'])
        layer.setCrs(core.QgsCoordinateReferenceSystem(int(d['epsg'])))
        s.setValue("Projections/defaultBehavior", defaultBehavior)
        if not layer.isValid():
            return False
        group = self.getGroupLayer()
        group.insertLayer(0, core.QgsProject.instance().addMapLayer(layer, False))
        return True