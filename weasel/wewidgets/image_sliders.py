__all__ = ['ImageSliders']

import pandas as pd

from PyQt5.QtCore import  Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QPushButton,
    )
from PyQt5.QtGui import QIcon

from .. import wewidgets as widgets

class ImageSliders(QWidget):
    """Widget with sliders to navigate through a DICOM series."""

    valueChanged = pyqtSignal()

    def __init__(self, series=None, image=None, tags=["AcquisitionTime", "SliceLocation"]):  
        super().__init__()

        self.sliderTags = tags

        self._setWidgets()
        self._setLayout()

        if series is not None:
            self.setData(series, image)

    def _setWidgets(self):

        self.slidersButton = QPushButton()
        self.slidersButton.setToolTip("Display Multiple Sliders")
        self.slidersButton.setCheckable(True)
        self.slidersButton.setIcon(QIcon(widgets.icons.slider_icon))
        self.slidersButton.clicked.connect(self._slidersButtonClicked)  

        self.instanceSlider = widgets.LabelSlider("", range(1))
        self.instanceSlider.valueChanged.connect(self._mainSliderValueChanged)

        self.sliders = [self.instanceSlider]

    def _setLayout(self):

        self.layout = QHBoxLayout()
        self.layout.setAlignment(Qt.AlignLeft  | Qt.AlignVCenter)
        self.layout.setSpacing(2)
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.addWidget(self.slidersButton)
        self.layout.addWidget(self.instanceSlider)

        self.setStyleSheet("background-color: white")
        self.setLayout(self.layout)

    def setData(self, series=None, image=None):

        self.series = series
        self._readDataFrame()
        self._setSliderValueLists()
        self.image = image
        if image is None:
            if self.series is not None:
                self.image = self.series.children(0)
        self._setSliderValues()
        self._sliderValueChanged()            

    def setSeries(self, series): # Obsolete?

        self.series = series
        self._readDataFrame()
        self._setSliderValueLists()
        self.image = self.series.children(0)
        self.setImage(self.image)

    def setImage(self, image):  # Obsolete?

        self.image = image
        self._setSliderValues()
        self._sliderValueChanged()

    def getSeries(self):

        return self.series

    def getImage(self):

        return self.image

    def _setSliderValueLists(self):

        for slider in self._activeSliders:
            values = self.dataFrame[slider.label].unique().tolist()
            values.sort()
            slider.setValues(values)

    def _readDataFrame(self):
        """Read the dataframe for the series.
        
        Drop tags that are not present in every instance. 
        Drop tags that appear only once.
        """
        # Add all default tags in the registry and get values
        tags = self.sliderTags.copy()  
        tags = list(set(tags + list(self.series.folder.dataframe)))
        if self.series is None:
            self.dataFrame = pd.DataFrame([], index=[], columns=tags)
        else:
            # If all required tags are in the register,
            # then just extract the register for the series;
            # else read the data from disk.
            if set(tags) == set(self.series.folder.dataframe):
                self.dataFrame = self.series.data()
            else: 
                self.dataFrame = self.series.read_dataframe(tags)  
        self.dataFrame.sort_values("InstanceNumber", inplace=True)
        self.dataFrame.dropna(axis=1, inplace=True)  
        self.dataFrame.reset_index()
        # remove tags with one unique value  
        for tag in self.sliderTags:        
            if tag in self.dataFrame: 
                values = self.dataFrame[tag].unique().tolist()
                if len(values) == 1:
                    self.dataFrame.drop(tag, axis=1, inplace=True)
        # update list of slider Tags
        for tag in self.sliderTags.copy():
            if tag not in self.dataFrame:
                self.sliderTags.remove(tag)

    def _slidersButtonClicked(self):
        """Show or hide the other sliders that can be added."""

        if self.slidersButton.isChecked(): 
            # Build Checkbox sliders
            self.slidersButton.setStyleSheet("background-color: red")
            for tag in self.sliderTags:
                tagValues = self.dataFrame[tag].unique().tolist()
                tagValues.sort()
                slider = widgets.CheckBoxSlider(tag, tagValues)
                slider.valueChanged.connect(self._sliderValueChanged)
                slider.stateChanged.connect(self._sliderStateChanged)
                self.layout.addWidget(slider)
                self.sliders.append(slider)
        else: 
            # Delete CheckBox sliders
            self.slidersButton.setStyleSheet(
                "background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #CCCCBB, stop: 1 #FFFFFF)"
            )
            for slider in self.sliders[1:]:
                slider.deleteLater()
            self.sliders = self.sliders[:1]
            self.sliders[0].show()

    def _sliderStateChanged(self):

        if self.image is None:
            self._sliderValueChanged()
        else:
            self._setActiveSliderValues()
            self._setMainSliderValue()

    def _setSliderValues(self):
        
        if self.image is None: return

        self._setActiveSliderValues()
        self._setMainSliderValue()

    def _setActiveSliderValues(self):

        if self.image is None: return

        find = self.dataFrame.SOPInstanceUID == self.image.UID[-1]
        row = self.dataFrame.loc[find]
        for slider in self._activeSliders:
            value = row[slider.label].values[0]
            slider.setValue(value)

    def _setMainSliderValue(self):

        if self.image is None: return

        imageUIDs = self._getAllSelectedImages()
        if len(imageUIDs) <= 1:
            self.sliders[0].hide()
        else:
            index = imageUIDs.index(self.image.UID[-1])
            self.sliders[0].setValue(index)
            self.sliders[0].show()

    def _mainSliderValueChanged(self):  
        """Change the selected image"""

        imageUIDs = self._getAllSelectedImages()
        index = self.sliders[0].value()
        self._set_image(imageUIDs[index])
        self.valueChanged.emit()

    def _sliderValueChanged(self):  
        """Change the selected image"""

        imageUIDs = self._getAllSelectedImages()
        if imageUIDs == []: 
            self.image = None
            self.sliders[0].hide()
        elif len(imageUIDs) == 1:
            #self.image = self.series.children(SOPInstanceUID = imageUIDs[0])[0]
            self._set_image(imageUIDs[0])
            self.sliders[0].hide()
        else:
            self.sliders[0].setValues(range(len(imageUIDs)))
            index = self.sliders[0].value()
            # self.image = self.series.children(SOPInstanceUID = imageUIDs[index])[0]
            self._set_image(imageUIDs[index])
            self.sliders[0].show()
        self.valueChanged.emit()

    def _set_image(self, SOPInstanceUID):
        """
        Set image based on its UID
        """
        df = self.dataFrame[self.dataFrame.SOPInstanceUID == SOPInstanceUID]
        self.image = self.series.dicm.object(self.series.folder, df.iloc[0], 4)
#        self.image = self.series.children(SOPInstanceUID = imageUIDs[index])[0]

    def _getAllSelectedImages(self):
        """Get the list of all image files selected by the optional sliders"""

        selection = pd.Series( 
            index = self.dataFrame.index, 
            data = self.dataFrame.shape[0] * [True]
        )
        for slider in self._activeSliders:
            sliderSelection = self.dataFrame[slider.label] == slider.value()
            selection = selection & sliderSelection
        if not selection.any():
            return []
        else:
            return self.dataFrame.SOPInstanceUID[selection].values.tolist()

    @property
    def _activeSliders(self):
        """Create a list of all active sliders"""

        activeSliders = []
        for slider in self.sliders[1:]:
            if slider.checkBox.isChecked():
                activeSliders.append(slider)
        return activeSliders