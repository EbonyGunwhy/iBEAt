__all__ = ['LabelSlider', 'CheckBoxSlider']

from PyQt5.QtCore import  Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QLabel, 
    QGroupBox, 
    QHBoxLayout,  
    QSlider, 
    QCheckBox, 
)

QGroupBoxStyleSheet = """
QGroupBox 
{
    border: 1px solid gray;
    border-radius: 2px;
    font-size: 9pt;
}
"""


class LabelSlider(QGroupBox):
    """A slider with a label to show the slider state.
    
    The checkbox carries a label that describes the values 
    navigated by the slider.  

    The application is the case where the label is a DICOM tag
    and the label Values are the unique values of that tag.
    """

    valueChanged = pyqtSignal()

    def __init__(self,  label, values): 
        super().__init__()

        self.label = label # E.g. KeyWord or (group, element) pair of the DICOM tag
        self.values = values # E.g. List of unique values for the DICOM tag

        self.labelWidget = QLabel()
        self.labelWidget.setToolTip("Navigate based on {}".format(label))
#        self.labelWidget.setMinimumWidth(140)
        self.labelWidget.adjustSize()

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setFocusPolicy(Qt.StrongFocus)  # This makes the slider work with arrow keys on Mac OS
        self.slider.setSingleStep(1)
        self.slider.setTickPosition(QSlider.TicksBothSides)
        self.slider.setTickInterval(1)
        self.slider.setMinimum(1)
        self.slider.setMaximum(len(values))
        self.slider.setValue(1)
        self.slider.valueChanged.connect(self.sliderValueChanged)
        
        self.layout = QHBoxLayout()
        self.layout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(2,0,2,0)
        self.layout.addWidget(self.slider)
        self.layout.addWidget(self.labelWidget)
        
        self.setStyleSheet(QGroupBoxStyleSheet)
        self.setFlat(True)
        self.setLayout(self.layout)

        self.setText()

    def sliderValueChanged(self):

        self.setText()
        self.valueChanged.emit()

    def setText(self):

        self.labelWidget.setText(
            str(self.label) + " " + str(self.value())
        )

    def setValues(self, values):

        previousValue = self.value()
        self.values = values
        self.slider.setMaximum(len(values))
        self.setValue(previousValue)

    def setValue(self, value):

        if value not in self.values: 
            value = self.values[0]
        index = self.values.index(value)
        self.slider.setValue(index+1)
        self.setText()

    def value(self):

        index = self.slider.value()
        return self.values[index-1]


class CheckBoxSlider(QGroupBox):
    """A slider with a checkbox to turn the slider on or off.
    
    The checkbox carries a label that describes the values 
    navigated by the slider.  

    The application is the case where the label is a DICOM tag
    and the label Values are the unique values of that tag.
    """

    stateChanged = pyqtSignal()
    valueChanged = pyqtSignal()

    def __init__(self,  label, values): 
        super().__init__()

        self.label = label # E.g. KeyWord or (group, element) pair of the DICOM tag
        self.values = values # E.g. List of unique values for the DICOM tag

        self.checkBox = QCheckBox()
        self.checkBox.setToolTip("Navigate based on {}".format(label))
        self.checkBox.setCheckState(Qt.Unchecked)
        self.checkBox.setMinimumWidth(160)
    #    self.checkBox.adjustSize()
        self.checkBox.stateChanged.connect(self.checkBoxStateChanged)

        self.slider = None
        
        self.layout = QHBoxLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(2,0,2,0)
        self.layout.insertWidget(1, self.checkBox)
        
        self.setStyleSheet(QGroupBoxStyleSheet)
        self.setFlat(True)
        self.setLayout(self.layout)

        self.setText()

    def setText(self):

        text = str(self.label)
        if self.slider is not None:
            text += ": " + str(self.value())
        self.checkBox.setText(text)

    def checkBoxStateChanged(self):

        if self.checkBox.isChecked():
            self.createSlider()  
        else:
            self.removeSlider()
        self.setText()
        self.stateChanged.emit()

    def createSlider(self): #use hide and show instead?

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setFocusPolicy(Qt.StrongFocus)  # This makes the slider work with arrow keys on Mac OS
        self.slider.setSingleStep(1)
        self.slider.setTickPosition(QSlider.TicksBothSides)
        self.slider.setTickInterval(1)
        self.slider.setMinimum(1)
        self.slider.setMaximum(len(self.values))
        self.slider.valueChanged.connect(self.sliderValueChanged)

        self.layout.insertWidget(0, self.slider)

    def sliderValueChanged(self):

        self.setText()
        self.valueChanged.emit()

    def removeSlider(self):
        
        self.slider.deleteLater()
        self.slider = None

    def setValues(self, values):

        previousValue = self.value()
        self.values = values
        self.slider.setMaximum(len(self.values))
        self.setValue(previousValue)

    def setValue(self, value):

        if value not in self.values: 
            value = self.values[0]
        index = self.values.index(value)
        self.slider.setValue(index+1)

    def value(self):

        index = self.slider.value()
        return self.values[index-1]