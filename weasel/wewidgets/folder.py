__all__ = ['DICOMFolderTree']

from PyQt5.QtCore import  Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QApplication, QAbstractItemView,
    QHeaderView, QTreeWidget, QTreeWidgetItem)

class DICOMFolderTree(QTreeWidget):
    """Displays a DICOM folder as a Tree."""

    itemSelectionChanged = pyqtSignal()

    def __init__(self, folder, status):
        super().__init__()
         
        self.status = status

        self.setAutoScroll(False)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setUniformRowHeights(True)
        self.setColumnCount(1)
        self.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.setHeaderLabels(["", ""])
        self.setContextMenuPolicy(Qt.CustomContextMenu)
#            self.itemDoubleClicked.connect(lambda item, col: self._displayImage(item, col))
        
        self.itemClicked.connect(lambda item, col: self._itemClickedEvent(item, col))
        self.setFolder(folder)

    def setFolder(self, folder=None):

        if folder is not None: 
            self.folder = folder

        QApplication.setOverrideCursor(Qt.WaitCursor)
        s = 0
        nr = len(self.folder.series())
        self.blockSignals(True)
        self.clear()
        self.folder.sortby(['StudyDate','SeriesNumber','AcquisitionTime'])
        for patient in self.folder.patients():
            patientWidgetItem = _treeWidgetItem(patient,  self)
            for study in patient.studies():
                studyWidgetItem = _treeWidgetItem(study, patientWidgetItem) 
                for series in study.series():
                    seriesWidgetItem = _treeWidgetItem(series, studyWidgetItem) 
                    self.status.progress(s, nr, "Building display..")
                    s += 1
        self.resizeColumnToContents(0) 
        self.blockSignals(False)
        self.status.hide()
        QApplication.restoreOverrideCursor()

    def _itemClickedEvent(self, item, col):
        """Update checked state of children and parents"""

        item.treeWidget().blockSignals(True)
        if col == 1:            
            selectedItems = self.selectedItems()
            if selectedItems:
                if len(selectedItems) == 1:
                    _toggle_checked(item) 
                    _save_checked(item)
                else: 
                    checked = selectedItems[0].checkState(0) == Qt.Checked
                    for i in selectedItems[1:]:
                        _set_checked(i, checked) 
                        _save_checked(i)            
        else:
            _save_checked(item)
            checked = item.checkState(0) == Qt.Checked
            _check_children(item, checked)
        _check_parents(item)
        item.treeWidget().blockSignals(False)
        self.itemSelectionChanged.emit()

    def uncheck_all(self):
        """Uncheck all TreeView items."""

        QApplication.setOverrideCursor(Qt.WaitCursor)
        root = self.invisibleRootItem()
        _check_children(root, False)
        self.folder.dataframe.checked = False
        QApplication.restoreOverrideCursor()
        self.itemSelectionChanged.emit()

def _treeWidgetItem(object, parent):
    """Build an item in the Tree"""

    return _buildTreeWidgetItem(parent, object, object.label(), object.is_checked())

def _buildSeriesTreeView(series, parent):

    df = series.data()
    checked = df.checked.all()
    parent = _buildTreeWidgetItem(parent, 
        object = series, 
        label = series.label(row=df.iloc[0]), 
        checked = checked,
        expanded = df.checked.any() and not checked,
    )
    for _, row in df.iterrows():
        instance = series.folder.object(row) # time limiting step
        _buildTreeWidgetItem(parent,  
            object = instance,
            label = instance.label(row), 
            checked = row.checked)
    
def _buildTreeWidgetItem(parent, object, label, checked, expanded=True):

    item = QTreeWidgetItem(parent)
    item.object = object
    item.setText(1, object.__class__.__name__ + " - {}".format(label))
    item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
    item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
    if checked:
        item.setCheckState(0, Qt.Checked)
    else:
        item.setCheckState(0, Qt.Unchecked)
    item.setExpanded(expanded)
    return item   

def _check_parents(item):
    """Check parents where all children are checked.
    """
    parent = item.parent()
    if parent:
        checked = parent.object.data().checked.all()
    #    checked = _all_children_checked(parent) # TEST!
        _set_check_state(parent, checked)
        _check_parents(parent)

def _all_children_checked(item):
    """Set the checkstate of all children of an item."""

    nrOfChildren = item.childCount()
    for n in range(nrOfChildren):
        child = item.child(n) 
        checked = child.checkState(0) == Qt.Checked
        if not checked: return False
    return True

def _toggle_checked(item):
    "Uncheck if checked and check if unchecked."

    checked = item.checkState(0) == Qt.Checked
    _set_checked(item, not checked)

def _set_checked(item, checked):
    """Check or uncheck an item"""

    _set_check_state(item, checked)
    _check_children(item, checked)

def _set_check_state(item, checked):
    """Ticks or unticks the box"""

    if checked: 
        item.setCheckState(0, Qt.Checked)
    else: 
        item.setCheckState(0, Qt.Unchecked)



def _save_checked(item): 
    """Save the item checked state."""

    files = item.object.files # SLOW
    checked = item.checkState(0) == Qt.Checked
    item.object.folder.dataframe.loc[files, 'checked'] = checked

def _check_children(item, checked):
    """Set the checkstate of all children of an item."""

    nrOfChildren = item.childCount()
    for n in range(nrOfChildren):
        child = item.child(n) 
        _set_checked(child, checked)  