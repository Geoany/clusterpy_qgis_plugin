# -*- coding: utf-8 -*-
"""
/***************************************************************************
 clusterpy_light
                                 A QGIS plugin
 Clusterpy plugin version for QGIS
                              -------------------
        begin                : 2014-01-24
        copyright            : (C) 2014 by RISE Group Universidad EAFIT
        email                : software@rise-group.org
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import QgsMessageBar
# Initialize Qt resources from file resources.py
import resources_rc
# Import the code for the dialog
from clusterpy_lightdialog import maxpDialog, minpDialog, aboutDialog
import os.path

from clusterpy import ClusterpyFeature, execmaxp, validtopology
from plugin_utils import addShapeToCanvas

class clusterpy_light:
    CLSP_MENU = u"&Clusterpy - Spatially constrained clustering"
    ERROR_MSG = u"There are features from the shapefile that are disconnected. \
                Check the following areas for errors in the geometry: "
    DONE_MSG = "Finish"

    def __init__(self, iface):
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value("locale/userLocale")[0:2]
        localePath = os.path.join(self.plugin_dir,
                                    'i18n',
                                    'clusterpy_light_{}.qm'.format(locale))

        if os.path.exists(localePath):
            self.translator = QTranslator()
            self.translator.load(localePath)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)
        # Create the dialog (after translation) and keep reference
        self.mc = self.iface.mapCanvas()
        self.maxpdlg = maxpDialog()
        self.maxpdlg.mc = self.mc

        self.aboutdlg = aboutDialog()
        #self.minpdlg = minpDialog()

    def initGui(self):
        default_icon = QIcon(":/uifiles/clusterpy.png")
        rise_icon = QIcon(":/uifiles/rise1.png")

        self.maxpaction = QAction(default_icon, u"Max-p Algorithm",
                                                    self.iface.mainWindow())
        self.maxpaction.triggered.connect(self.maxp)

        #self.minpaction = QAction(default_icon, u"Min-p Algorithm",
                                                    #self.iface.mainWindow())
        #self.minpaction.triggered.connect(self.minp)
        self.aboutaction = QAction(rise_icon, u"About RISE",
                                                    self.iface.mainWindow())
        self.aboutaction.triggered.connect(self.about)

        self.iface.addPluginToMenu(self.CLSP_MENU, self.maxpaction)
        self.iface.addPluginToMenu(self.CLSP_MENU, self.aboutaction)
        #self.iface.addPluginToMenu(self.CLSP_MENU, self.minpaction)

    def unload(self):
        self.iface.removePluginMenu(self.CLSP_MENU, self.maxpaction)
        self.iface.removePluginMenu(self.CLSP_MENU, self.aboutaction)
        #self.iface.removePluginMenu(self.CLSP_MENU, self.minpaction)

    def about(self):
        self.aboutdlg.show()

    def maxp(self):
        self.maxpdlg.show()
        self.maxpdlg.layer_combo.clear()
        self.maxpdlg.layer_combo.addItems([x.name() for x in self.mc.layers()])
        result = self.maxpdlg.exec_()
        layerindex = self.maxpdlg.layer_combo.currentIndex()
        if result == 1 and layerindex > -1:
            layerindex = self.maxpdlg.layer_combo.currentIndex()
            messagebar = self.iface.messageBar()
            attrname = self.maxpdlg.attribute_combo.currentText()
            thresholdattr = self.maxpdlg.threshold_attr_combo.currentText()
            threshold = self.maxpdlg.threshold_spin.value()
            maxit = self.maxpdlg.maxit_spin.value()
            tabumax = self.maxpdlg.tabumax_spin.value()
            tabusize = self.maxpdlg.tabulength_spin.value()

            output_path = self.maxpdlg.layer_path.text()
            layer = self.mc.layer(layerindex)
            provider = layer.dataProvider()
            maxpfield = QgsField(name = "MAXP", type = 2)
            newfields = QgsFields()
            newfields.extend(provider.fields())
            newfields.append(maxpfield)

            clspyfeatures = {}
            for feat in provider.getFeatures():
                uid = feat.id()
                featids = []
                for _ftr in provider.getFeatures():
                    if feat != _ftr and feat.geometry().touches(_ftr.geometry()):
                        featids.append(_ftr.id())
                neighbors = set(featids)
                neighbors.discard(uid)
                thresholdval = feat.attribute(thresholdattr)
                attributeval = feat.attribute(attrname)
                clspyfeatures[uid] = ClusterpyFeature(uid, thresholdval,
                                                    neighbors, attributeval)

            valid, islands = validtopology(clspyfeatures)
            if not valid:
                self.showMessage("Topology Error",
                            self.ERROR_MSG + str(islands),
                            level=QgsMessageBar.CRITICAL)
                return
            regions = execmaxp(clspyfeatures,
                                    threshold,
                                    maxit,
                                    tabusize,
                                    tabumax)

            newlayer = QgsVectorFileWriter( output_path,
                                            None,
                                            newfields,
                                            provider.geometryType(),
                                            provider.crs())

            for area in layer.getFeatures():
                newarea = QgsFeature()
                newarea.setGeometry(area.geometry())
                attrs = area.attributes()
                attrs.append(regions[area.id()])
                newarea.setAttributes(attrs)
                newlayer.addFeature(newarea)

            del newlayer
            if self.maxpdlg.addToCanvas():
                addShapeToCanvas(output_path)
            self.showMessage("Clusterpy", self.DONE_MSG, duration = 3)

    def showMessage(self, msgtype, msgtext, level=QgsMessageBar.INFO,
                                            duration=None):
        messagebar = self.iface.messageBar()
        messagebar.pushMessage(msgtype, msgtext, level=level, duration=duration)

    def minp(self):
    #    # show the dialog
    #    self.minpdlg.show()
    #    # Run the dialog event loop
    #    result = self.minpdlg.exec_()
    #    # See if OK was pressed
    #    if result == 1:
            pass
