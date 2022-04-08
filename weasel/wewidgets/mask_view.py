__all__ = [
    'MaskView', 
    'MaskViewBrush', 
    'MaskViewPenFreehand',
    'MaskViewPenRectangle', 
    'MaskViewPenPolygon', 
    'MaskViewPenCircle'
]

import math
import numpy as np
from matplotlib.path import Path as MplPath

from PyQt5.QtCore import Qt, QPointF, QRectF, pyqtSignal
from PyQt5.QtGui import QPixmap, QImage, qRgb, QIcon, QCursor, QColor, QPen
from PyQt5.QtWidgets import QGraphicsObject, QAction, QAction, QMenu

from .. import wewidgets as widgets


class MaskView(widgets.ImageView):
    """Extends image view with a MaskItem for drawing masks.
    
    If no mask instance is provided, this creates
    a canvas that can be drawn on
    but the results can't be saved or retrieved."""

    newMask = pyqtSignal()

    def __init__(self, image=None, mask=None): 
        super().__init__(image)
      
        shape = self._shape(mask)
        self.maskItem = MaskItem(mask, shape)
        self.maskItem.newMask.connect(self._newMask)
        self.scene.addItem(self.maskItem)

    @property
    def mask(self):
        return self.maskItem.mask

    def _shape(self, mask): # private

        if mask is None:
            width = self.imageItem.pixMap.width()
            height = self.imageItem.pixMap.height() 
        else:            
            width = mask.Rows
            height = mask.Columns
        return width, height

#    def isBlank(self):

#        nrMaskPixels = np.count_nonzero(self.maskItem.bin)
#        return nrMaskPixels == 0

    def setObject(self, mask):
        self.maskItem.mask = mask
        
    def setMask(self, mask):

        self._updatePixelArray()
        shape = self._shape(mask)
        self.maskItem.mask = mask
        self.maskItem._setMaskImage(shape)

    def getMask(self):

        return self.mask

#    def getPixelArray(self):
#        return self.maskItem._getMaskImage()

    def _updatePixelArray(self):
        """Write the current pixel array in the mask image"""

        if self.mask is None: return
        array = self.maskItem._getMaskImage()
        self.mask.set_array(array)

    def eraseMask(self): # not yet in use

        self.maskItem.eraseMaskImage()
        self._updatePixelArray()

    def _newMask(self):

        mask = self.image.copy()
        mask.WindowCenter = 1
        mask.WindowWidth = 2
        self.maskItem.mask = mask
        self._updatePixelArray()
        self.newMask.emit()


class MaskItem(QGraphicsObject):
    """Displays a mask as an overlay on an image.
    """

    newMask = pyqtSignal()

    def __init__(self, mask, shape): 
        super().__init__()

        self.mask = mask
        self._setMaskImage(shape)

    def _setMaskImage(self, shape=(128,128)):

        if self.mask is None:
            self.bin = np.zeros(shape, dtype=bool)
        else:
            self.bin = self.mask.array() != 0
        self.qImage = QImage(self.bin.shape[0], self.bin.shape[1], QImage.Format_RGB32)
        self.fillQImage()
        self.update()

    def _getMaskImage(self):

        return self.bin.astype(float)

    def eraseMaskImage(self):

        self.bin.fill(False)
        self.fillQImage()

    def boundingRect(self): 
        """Abstract method - must be overridden."""

        return QRectF(0, 0, self.bin.shape[0], self.bin.shape[1])

    def paint(self, painter, option, widget):
        """Executed by GraphicsView when calling update()"""

        pixMap = QPixmap.fromImage(self.qImage)
        width = pixMap.width()
        height = pixMap.height()
        painter.setOpacity(0.25)
        painter.drawPixmap(0, 0, width, height, pixMap)
 
    def fillQImage(self):

        for x in range(self.bin.shape[0]):
            for y in range(self.bin.shape[1]):
                self.setPixel(x, y)

    def setPixel(self, x, y, add=None):

        if add is None:
            add = self.bin[x, y]
        else:
            self.bin[x,y] = add
        if add: 
            red = 255
            if self.mask is None:
                self.newMask.emit()
        else:
            red = 0
        color = qRgb(red, 0, 0)
        self.qImage.setPixel(x, y, color)


class MaskViewBrush(widgets.ImageViewCursor):
    """Painting or erasing tool.
    
    Features
    --------
    >>> Left click and drag to paint or erase.
    >>> Right click to change the brush properties
    (erase or paint, size of the brush).
    >>> Right click and drag to change the windowing.
    """

    def __init__(self, brushSize=1, mode="paint"):
        super().__init__()

        self.setBrushSize(brushSize)
        self.setMode(mode)

    def setView(self, imageView):
        """Assign an ImageView instance to handle"""

        super().setView(imageView)
        self.maskItem = imageView.maskItem

    def setBrushSize(self, brushSize):

        self.brushSize = brushSize

    def setMode(self, mode):

        self.mode = mode
        if mode == "paint":
            pixMap = QPixmap(widgets.icons.paint_brush)
            self.cursor = QCursor(pixMap, hotX=0, hotY=16)
            self.toolTip = 'Paint brush'
        elif mode == "erase":
            pixMap = QPixmap(widgets.icons.eraser)
            self.cursor = QCursor(pixMap, hotX=0, hotY=16)
            self.toolTip = 'Eraser'
        self.icon = QIcon(pixMap)

    def itemMousePressEvent(self, event):

        self.x = int(event.pos().x())
        self.y = int(event.pos().y())
        button = event.button()
        if button == Qt.LeftButton:
            self.paintPixels()
        elif button == Qt.RightButton:
            self.launchContextMenu(event)

    def itemMouseReleaseEvent(self, event):

        self.x = int(event.pos().x())
        self.y = int(event.pos().y())

    def itemMouseMoveEvent(self, event):

        self.x = int(event.pos().x())
        self.y = int(event.pos().y())
        buttons = event.buttons()
        if buttons == Qt.LeftButton:
            self.paintPixels()  
        self.view.mousePositionMoved.emit()

    def paintPixels(self):
   
        w = int((self.brushSize - 1)/2)
        for x in range(self.x-w, self.x+w+1, 1):
            if 0 <= x < self.maskItem.bin.shape[0]:
                for y in range(self.y-w, self.y+w+1, 1):
                    if 0 <= y < self.maskItem.bin.shape[1]:
                        self.maskItem.setPixel(x, y, self.mode == "paint")
        self.maskItem.update()
       
    def launchContextMenu(self, event):

        pickBrush = QAction(QIcon(widgets.icons.paint_brush), 'Paint', None)
        pickBrush.setCheckable(True)
        pickBrush.setChecked(self.mode == "paint")
        pickBrush.triggered.connect(lambda: self.setMode("paint"))
        
        pickEraser = QAction(QIcon(widgets.icons.eraser), 'Erase', None)
        pickEraser.setCheckable(True)
        pickEraser.setChecked(self.mode == "erase")
        pickEraser.triggered.connect(lambda: self.setMode("erase"))

        clearMask = QAction(QIcon(widgets.icons.arrow_curve_180_left), 'Clear Region', None)
        clearMask.triggered.connect(self.maskItem.eraseMaskImage)

        onePixel = QAction('1 pixel', None)
        onePixel.setCheckable(True)
        onePixel.setChecked(self.brushSize == 1)
        onePixel.triggered.connect(lambda: self.setBrushSize(1))

        threePixels = QAction('3 pixels', None)
        threePixels.setCheckable(True)
        threePixels.setChecked(self.brushSize == 3)
        threePixels.triggered.connect(lambda: self.setBrushSize(3))

        fivePixels = QAction('5 pixels', None)
        fivePixels.setCheckable(True)
        fivePixels.setChecked(self.brushSize == 5)
        fivePixels.triggered.connect(lambda: self.setBrushSize(5))

        sevenPixels = QAction('7 pixels', None)
        sevenPixels.setCheckable(True)
        sevenPixels.setChecked(self.brushSize == 7)
        sevenPixels.triggered.connect(lambda: self.setBrushSize(7))

        ninePixels = QAction('9 pixels', None)
        ninePixels.setCheckable(True)
        ninePixels.setChecked(self.brushSize == 9)
        ninePixels.triggered.connect(lambda: self.setBrushSize(9))

        elevenPixels = QAction('11 pixels', None)
        elevenPixels.setCheckable(True)
        elevenPixels.setChecked(self.brushSize == 11)
        elevenPixels.triggered.connect(lambda: self.setBrushSize(11))

        twentyOnePixels = QAction('21 pixels', None)
        twentyOnePixels.setCheckable(True)
        twentyOnePixels.setChecked(self.brushSize == 21)
        twentyOnePixels.triggered.connect(lambda: self.setBrushSize(21))

        contextMenu = QMenu()
        contextMenu.addAction(pickBrush)
        contextMenu.addAction(pickEraser)
        contextMenu.addAction(clearMask)

        subMenu = contextMenu.addMenu('Brush size')
        subMenu.setEnabled(True)
        # subMenu.clear()
        subMenu.addAction(onePixel)
        subMenu.addAction(threePixels)
        subMenu.addAction(fivePixels)
        subMenu.addAction(sevenPixels)
        subMenu.addAction(ninePixels)
        subMenu.addAction(elevenPixels)
        subMenu.addAction(twentyOnePixels)

        contextMenu.exec_(event.screenPos())


class MaskViewPenFreehand(widgets.ImageViewCursor):
    """Freehand region drawing tool.
    
    Features
    --------
    >>> Left click and drag to draw, release to close
    >>> Right click to change the pen properties
    """

    def __init__(self, mode="draw"):
        super().__init__()

        self.icon = QIcon(widgets.icons.layer_shape_curve)
        self.path = None
        self.setMode(mode)
        
    def setMode(self, mode):

        self.mode = mode
        if mode == "draw":
            pixMap = QPixmap(widgets.icons.pencil)
            self.cursor = QCursor(pixMap, hotX=0, hotY=16)
            self.toolTip = 'Draw'
        elif mode == "cut":
            pixMap = QPixmap(widgets.icons.cutter)
            self.cursor = QCursor(pixMap, hotX=0, hotY=16)
            self.toolTip = 'Cut'

    def setView(self, imageView):
        """Assign an ImageView instance to handle"""

        super().setView(imageView)
        self.maskItem = imageView.maskItem
        
    def paint(self, painter, option, widget):

        if self.path is None: return

        pen = QPen()
        pen.setColor(QColor(Qt.white))
        pen.setWidth(0)
        painter.setPen(pen)

        position = self.path[0]
        p1 = QPointF(position[0], position[1])
        for position in self.path[1:]:
            p2 = QPointF(position[0], position[1])
            painter.drawLine(p1, p2)
            p1 = p2
        position = self.path[0]
        p2 = QPointF(position[0], position[1])
        painter.drawLine(p1, p2)

    def itemMousePressEvent(self, event):

        self.x = int(event.pos().x())
        self.y = int(event.pos().y())
        if event.button() == Qt.LeftButton:
            position = [event.pos().x(), event.pos().y()]
            self.path = [position]
        elif event.button() == Qt.RightButton:
            self.launchContextMenu(event)

    def itemMouseReleaseEvent(self, event):
        
        self.x = int(event.pos().x())
        self.y = int(event.pos().y())
        button = event.button()
        if button == Qt.LeftButton:
            if self.path is not None:
                self.fillPath()
                self.path = None
            
    def itemMouseMoveEvent(self, event):

        self.x = int(event.pos().x())
        self.y = int(event.pos().y())
        buttons = event.buttons()
        if buttons == Qt.LeftButton:
            position = [event.pos().x(), event.pos().y()]
            if position not in self.path:
                self.path.append(position)
                self.item.update()

    def fillPath(self):

        if len(self.path) == 0: return
        roiPath = MplPath(self.path, closed=True)
        nx, ny = self.maskItem.bin.shape[0], self.maskItem.bin.shape[1]
        x, y = np.meshgrid(np.arange(0.5, 0.5+nx), np.arange(0.5, 0.5+ny))
        points = list(zip(x.flatten(),y.flatten()))
        bin = roiPath.contains_points(points, radius=0.0).reshape((nx, ny))  
        bin = np.transpose(bin != 0)
        #bin = bin != 0
        if self.mode == "draw":
            self.maskItem.bin = np.logical_or(self.maskItem.bin, bin)
        elif self.mode == "cut":
            self.maskItem.bin = np.logical_and(self.maskItem.bin, np.logical_not(bin))
        self.maskItem.fillQImage()
        self.maskItem.update()
        
    def launchContextMenu(self, event):

        pickBrush = QAction(QIcon(widgets.icons.pencil), 'Draw', None)
        pickBrush.setCheckable(True)
        pickBrush.setChecked(self.mode == "draw")
        pickBrush.triggered.connect(lambda: self.setMode("draw"))
        
        pickEraser = QAction(QIcon(widgets.icons.cutter), 'Cut', None)
        pickEraser.setCheckable(True)
        pickEraser.setChecked(self.mode == "cut")
        pickEraser.triggered.connect(lambda: self.setMode("cut"))

        clearMask = QAction(QIcon(widgets.icons.arrow_curve_180_left), 'Clear mask', None)
        clearMask.triggered.connect(self.maskItem.eraseMaskImage)

        contextMenu = QMenu()
        contextMenu.addAction(pickBrush)
        contextMenu.addAction(pickEraser)
        contextMenu.addAction(clearMask)
        contextMenu.exec_(event.screenPos())


class MaskViewPenPolygon(MaskViewPenFreehand):
    """Polygon region drawing tool.
    
    Features
    --------
    >>> Left click and drag to draw, release to close
    >>> Right click to change the pen properties
    """

    def __init__(self, mode="draw"):
        super().__init__(mode=mode)

        self.icon = QIcon(widgets.icons.layer_shape_polygon)

    def itemHoverMoveEvent(self, event):

        if self.path is not None:
            self.path[-1] = [event.pos().x(), event.pos().y()]
            self.maskItem.update()
        super().itemHoverMoveEvent(event)

    def itemMousePressEvent(self, event):

        self.x = int(event.pos().x())
        self.y = int(event.pos().y())
        if event.button() == Qt.LeftButton:
            position = [event.pos().x(), event.pos().y()]
            if self.path is None:
                self.path = [position, position]
            else:
                self.path[-1] = position
                self.path.append(position)
        elif event.button() == Qt.RightButton:
            self.launchContextMenu(event)

    def itemMouseReleaseEvent(self, event):
        pass

    def itemMouseMoveEvent(self, event):

        self.x = int(event.pos().x())
        self.y = int(event.pos().y())
        self.path[-1] = [event.pos().x(), event.pos().y()]
        self.maskItem.update()

    def itemMouseDoubleClickEvent(self, event):

        self.x = int(event.pos().x())
        self.y = int(event.pos().y())
        button = event.button()
        if button == Qt.LeftButton:
            if self.path is not None:
                self.path[-1] = [event.pos().x(), event.pos().y()]
                self.fillPath()
                self.maskItem.update()
                self.path = None


class MaskViewPenRectangle(MaskViewPenFreehand):
    """Rectangle region drawing tool.
    
    Features
    --------
    >>> Left click and drag to draw, release to close
    >>> Right click to change the pen properties
    """

    def __init__(self, mode="draw"):
        super().__init__(mode=mode)

        self.icon = QIcon(widgets.icons.layer_shape)
            
    def itemMouseMoveEvent(self, event):

        self.x = int(event.pos().x())
        self.y = int(event.pos().y())
        buttons = event.buttons()
        if buttons == Qt.LeftButton:
            corner1 = self.path[0]
            corner2 = [event.pos().x(), event.pos().y()]
            self.path = [
                [corner1[0], corner1[1]], 
                [corner2[0], corner1[1]], 
                [corner2[0], corner2[1]],
                [corner1[0], corner2[1]],
                [corner1[0], corner1[1]]]
            self.maskItem.update()


class MaskViewPenCircle(MaskViewPenFreehand):
    """Rectangle region drawing tool.
    
    Features
    --------
    >>> Left click and drag to draw, release to close
    >>> Right click to change the pen properties
    """

    def __init__(self, mode="draw"):
        super().__init__(mode=mode)

        self.icon = QIcon(widgets.icons.layer_shape_ellipse)
        self.center = None

    def itemMousePressEvent(self, event):

        self.x = int(event.pos().x())
        self.y = int(event.pos().y())
        if event.button() == Qt.LeftButton:
            self.center = [event.pos().x(), event.pos().y()]
        elif event.button() == Qt.RightButton:
            self.launchContextMenu(event)
            
    def itemMouseMoveEvent(self, event):

        self.x = int(event.pos().x())
        self.y = int(event.pos().y())
        buttons = event.buttons()
        if buttons == Qt.LeftButton:
            p = [event.pos().x(), event.pos().y()]
            self.setCirclePath(p)
            self.maskItem.update()

    def setCirclePath(self, p):
        """Return a circle with center in c and going through point p"""

        c = self.center
        pc = [p[0]-c[0], p[1]-c[1]]
        radius = math.sqrt(pc[0]**2 + pc[1]**2)
        if radius == 0: return
        step = 0.5 # pixel - precision of the circle
        if step > radius: step = radius
        angle = math.acos(1-0.5*(step/radius)**2)
        nsteps = round(2*math.pi/angle)
        angle = 2*math.pi/nsteps
        x0 = pc[0]
        y0 = pc[1]
        self.path = [p]
        for _ in range(nsteps):
            x = math.cos(angle)*x0 - math.sin(angle)*y0
            y = math.sin(angle)*x0 + math.cos(angle)*y0
            self.path.append([c[0] + x, c[1] + y])
            x0 = x
            y0 = y
