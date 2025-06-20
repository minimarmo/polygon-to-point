from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
from qgis.core import (
    QgsProject, QgsVectorFileWriter, QgsWkbTypes,
    QgsFields, QgsField, QgsFeature, QgsVectorLayer
)
from PyQt5.QtWidgets import QCheckBox, QLineEdit, QWidget, QHBoxLayout, QTableWidgetItem, QMessageBox
from PyQt5.QtCore import Qt, QVariant

# Initialize Qt resources from file resources.py
from .resources_rc import *
# Import the code for the dialog
from .PolygonToPoint_dialog import PolygonToPointDialog
import os.path


class PolygonToPoint:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'PolygonToPoint_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Polygon to Point')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('PolygonToPoint', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = os.path.join(self.plugin_dir, 'icon.png')
        self.add_action(
            icon_path,
            text=self.tr(u'Polygon to Point'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Polygon to Point'),
                action)
            self.iface.removeToolBarIcon(action)

    def populate_layers(self):
        self.dlg.layerComboBox.clear()
        layers = [l for l in QgsProject.instance().mapLayers().values() if l.type() == 0]
        for layer in layers:
            self.dlg.layerComboBox.addItem(layer.name())
        self.populate_fields()  # โหลด field สำหรับเลเยอร์แรก

    def populate_fields(self):
        self.dlg.fieldRenameTable.setRowCount(0)
        layer_name = self.dlg.layerComboBox.currentText()
        layer = next((l for l in QgsProject.instance().mapLayers().values() if l.name() == layer_name), None)

        if not layer:
            return

        fields = layer.fields()
        self.dlg.fieldRenameTable.setRowCount(len(fields))

        for i, field in enumerate(fields):
            # Checkbox
            chk = QCheckBox()
            chk_widget = QWidget()
            layout = QHBoxLayout(chk_widget)
            layout.addWidget(chk)
            layout.setAlignment(Qt.AlignCenter)
            layout.setContentsMargins(0, 0, 0, 0)
            self.dlg.fieldRenameTable.setCellWidget(i, 0, chk_widget)

            # Field name (readonly)
            self.dlg.fieldRenameTable.setItem(i, 1, QTableWidgetItem(field.name()))

            # New name (editable)
            new_name_edit = QLineEdit(field.name())
            self.dlg.fieldRenameTable.setCellWidget(i, 2, new_name_edit)
    
    def get_selected_fields_with_new_names(self):
        table = self.dlg.fieldRenameTable
        selected = []
        for row in range(table.rowCount()):
            chk_widget = table.cellWidget(row, 0)
            chk = chk_widget.findChild(QCheckBox) if chk_widget else None
            if chk and chk.isChecked():
                old_name = table.item(row, 1).text()
                new_name = table.cellWidget(row, 2).text()
                selected.append((old_name, new_name))
        return selected

    def run_export(self):
        layer_name = self.dlg.layerComboBox.currentText()
        is_gpkg = self.dlg.radioGpkg.isChecked()

        layer = next((l for l in QgsProject.instance().mapLayers().values() if l.name() == layer_name), None)
        if not layer:
            QMessageBox.warning(None, "Error", "ไม่พบเลเยอร์")
            return

        selected_fields = self.get_selected_fields_with_new_names()
        if not selected_fields:
            QMessageBox.warning(None, "Error", "กรุณาเลือกฟิลด์อย่างน้อย 1 รายการ")
            return
        
        new_names = [new for _, new in selected_fields]
        if len(new_names) != len(set(new_names)):
            QMessageBox.warning(None, "Error", "มีชื่อคอลัมน์ซ้ำกัน กรุณาตั้งชื่อให้ไม่ซ้ำ")
            return

        # ตั้ง path
        downloads_path = os.path.join(os.path.expanduser('~'), 'Downloads')
        base_name = layer_name + "_point"
        ext = ".gpkg" if is_gpkg else ".shp"
        output_path = os.path.join(downloads_path, base_name + ext)

        # Field definition
        fields = QgsFields()
        for _, new_name in selected_fields:
            fields.append(QgsField(new_name, QVariant.String))

        writer = QgsVectorFileWriter(
            output_path, "UTF-8", fields,
            QgsWkbTypes.Point, layer.sourceCrs(),
            "GPKG" if is_gpkg else "ESRI Shapefile"
        )

        for feat in layer.getFeatures():
            geom = feat.geometry()
            if geom:
                pt = geom.centroid()
                new_feat = QgsFeature()
                new_feat.setGeometry(pt)
                attrs = [str(feat[old]) for old, _ in selected_fields]
                new_feat.setAttributes(attrs)
                writer.addFeature(new_feat)

        del writer

        new_layer = QgsVectorLayer(output_path, base_name, "ogr")
        if new_layer.isValid():
            QgsProject.instance().addMapLayer(new_layer)
            QMessageBox.information(None, "สำเร็จ", f"สร้างไฟล์ใหม่แล้วที่:\n{output_path}")
            self.dlg.close()
        else:
            QMessageBox.warning(None, "Error", "ไม่สามารถโหลดไฟล์ใหม่เข้า QGIS ได้")


    def run(self):
        """Run method that performs all the real work"""

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False
            self.dlg = PolygonToPointDialog()
            self.populate_layers()
            self.dlg.layerComboBox.currentIndexChanged.connect(self.populate_fields)
            self.dlg.runButton.clicked.connect(self.run_export)

        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass
