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
# Initialize Qt resources from file resources.py
import resources_rc
# Import the code for the dialog
from clusterpy_lightdialog import maxpDialog, minpDialog
import os.path

class clusterpy_light:
    CLSP_MENU = u"&Clusterpy - Spatially constrained clustering"

    def __init__(self, iface):
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value("locale/userLocale")[0:2]
        localePath = os.path.join(self.plugin_dir, 'i18n', 'clusterpy_light_{}.qm'.format(locale))

        if os.path.exists(localePath):
            self.translator = QTranslator()
            self.translator.load(localePath)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)
        # Create the dialog (after translation) and keep reference
        self.mc = self.iface.mapCanvas()
        self.maxpdlg = maxpDialog()
        self.maxpdlg.mc = self.mc

        #self.minpdlg = minpDialog()

    def initGui(self):
        default_icon = QIcon(":/plugins/clusterpy_light/icon.png")

        self.maxpaction = QAction(default_icon, u"Max-p Algorithm",
                                                    self.iface.mainWindow())
        self.maxpaction.triggered.connect(self.maxp)

        self.minpaction = QAction(default_icon, u"Min-p Algorithm",
                                                    self.iface.mainWindow())
        self.minpaction.triggered.connect(self.minp)

        self.iface.addPluginToMenu(self.CLSP_MENU, self.maxpaction)
        self.iface.addPluginToMenu(self.CLSP_MENU, self.minpaction)

    def unload(self):
        self.iface.removePluginMenu(self.CLSP_MENU, self.maxpaction)
        self.iface.removePluginMenu(self.CLSP_MENU, self.minpaction)

    def maxp(self):
        self.maxpdlg.show()
        self.maxpdlg.layer_combo.clear()
        self.maxpdlg.layer_combo.addItems([x.name() for x in self.mc.layers()])

        result = self.maxpdlg.exec_()
        # See if OK was pressed
        if result == 1:
            pass

    #def minp(self):
    #    # show the dialog
    #    self.minpdlg.show()
    #    # Run the dialog event loop
    #    result = self.minpdlg.exec_()
    #    # See if OK was pressed
    #    if result == 1:
    #        pass
