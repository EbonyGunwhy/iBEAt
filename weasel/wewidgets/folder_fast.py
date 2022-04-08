__all__ = ['DICOMFolderTree']

from PyQt5.QtCore import  Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QApplication, QAbstractItemView,
    QHeaderView, QTreeWidget, QTreeWidgetItem,
)

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
            self.folder=folder

        QApplication.setOverrideCursor(Qt.WaitCursor)
        self.blockSignals(True)
        self.clear()
        self.folder.sortby(['StudyDate','SeriesNumber','AcquisitionTime'])

        # return a view of the data that are not removed
        current = self.folder.dataframe.removed == False
        df = self.folder.dataframe.loc[current]

        nr = len(df.SeriesInstanceUID.unique())
        cnt = 0
        for patient in df.PatientID.unique():
            df_patient = df.loc[df.PatientID == patient]
            label = self.folder.label(df_patient.iloc[0], 'Patient')
            patientWidget = _treeWidgetItem(df_patient.iloc[0], self, label)
            for study in df_patient.StudyInstanceUID.unique():
                df_study = df_patient.loc[df_patient.StudyInstanceUID == study]
                label = self.folder.label(df_study.iloc[0], 'Study') # replace by dbd.label()
                studyWidget = _treeWidgetItem(df_study.iloc[0], patientWidget, label) 
                for sery in df_study.SeriesInstanceUID.unique():
                    df_series = df_study.loc[df_study.SeriesInstanceUID == sery]
                    label = self.folder.label(df_series.iloc[0], 'Series')
                    seriesWidget =  _treeWidgetItem(df_series.iloc[0], studyWidget, label)
                    self.status.progress(cnt, nr, "Building display..")
                    cnt += 1

        self.status.hide()
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
                    checked = item.checkState(0) == Qt.Checked
                    self.uncheck_all()
                    _set_checked(item, not checked)
                else:
                    self.uncheck_all()
                    for i in selectedItems:
                        _set_checked(i, True) 
        else:
            checked = item.checkState(0) == Qt.Checked
            _check_children(item, checked)
        item.treeWidget().blockSignals(False)
        self.itemSelectionChanged.emit()

    def uncheck_all(self):
        """Uncheck all TreeView items."""

        QApplication.setOverrideCursor(Qt.WaitCursor)
        root = self.invisibleRootItem()
        _check_children(root, False)
        QApplication.restoreOverrideCursor()
        self.itemSelectionChanged.emit()

    def get_selected(self, generation=1):

        try:
            root = self.invisibleRootItem()
        except RuntimeError:
            return []
        items = _children([root])
        while generation > 1:
            items = _children(items)
            generation -= 1
        return [i.row for i in items if i.checkState(0)==Qt.Checked]

def _treeWidgetItem(row, parent, label, expanded=True):
    """Build an item in the Tree"""

    item = QTreeWidgetItem(parent)
    item.row = row
    item.setText(1, label)
    item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
    item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
    item.setCheckState(0, Qt.Unchecked)
    item.setExpanded(expanded)
    return item 

def _set_checked(item, checked):
    """Check or uncheck an item"""

    if checked: 
        item.setCheckState(0, Qt.Checked)
    else: 
        item.setCheckState(0, Qt.Unchecked)
    _check_children(item, checked)


def _children(items):

    children = []
    for item in items:
        cnt = item.childCount()
        children += [item.child(i) for i in range(cnt)]
    #    for n in range(nrOfChildren):
    #        child = item.child(n)
    #        children.append(child)
    return children

def _check_children(item, checked):
    """Set the checkstate of all children of an item."""

    for child in _children([item]):
        _set_checked(child, checked)