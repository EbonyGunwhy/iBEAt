__all__ = ['ImageView', 'ImageViewCursor', 'ImageViewZoom']

from PyQt5.QtCore import Qt, pyqtSignal, QRectF
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsObject
from PyQt5.QtGui import QPixmap, QCursor, QIcon, QColor, QPen, QBrush

from . import icons

class ImageView(QGraphicsView):
    """Wrapper for ImageItem displaying it in a scrollable Widget"""

    imageUpdated = pyqtSignal()
    mousePositionMoved = pyqtSignal()

    def __init__(self, image=None): 
        super().__init__()
      
        self.imageItem = ImageItem(image)
        self.scene = QGraphicsScene(self)
        self.scene.addItem(self.imageItem)
        self.setScene(self.scene)
        self.setBackgroundBrush(QBrush(Qt.black))
        self.fitInView(self.imageItem, Qt.KeepAspectRatio)

    def setEventHandler(self, eventHandler):

        self.eventHandler = eventHandler
        eventHandler.setView(self)
        
    def setData(self, image):

        self.imageItem.setData(image)

    def getImage(self):

        return self.imageItem.image

    @property
    def image(self):

        return self.imageItem.image


class ImageItem(QGraphicsObject):
    """Displays a mask as an overlay on an image.
    
    Needs to be assigned an image to display, but a mask is optional.
    If no mask is provided, a mask will be created from the image.
    """

    def __init__(self, image): 
        super().__init__()

        self.boundingRectangle = QRectF(0, 0, 128, 128)
        self.eventHandler = None
        self.setData(image)

    def setData(self, image):

        if image is not None:
            self.boundingRectangle = QRectF(0, 0, image.Columns, image.Rows)
        self.image = image
        self._setPixMap()
        self.update()

    def boundingRect(self): 
        """Abstract method - must be overridden."""

        return self.boundingRectangle

    def _setPixMap(self):

        if self.image is None:
            width = int(self.boundingRectangle.width())
            height = int(self.boundingRectangle.height())
            self.pixMap = QPixmap(width, height)
            self.pixMap.fill(Qt.black)
        else:
            self.qImage = self.image.QImage()
            self.pixMap = QPixmap.fromImage(self.qImage)

    def paint(self, painter, option, widget):
        """Executed by GraphicsView when calling update()"""

        width = self.pixMap.width()
        height = self.pixMap.height()
        painter.drawPixmap(0, 0, width, height, self.pixMap)
        if self.eventHandler is not None:
            self.eventHandler.paint(painter, option, widget)

    def setEventHandler(self, eventHandler):

        self.eventHandler = eventHandler

    #
    # Delegate all event handling to the event handler
    #

    def hoverEnterEvent(self, event):

        if self.eventHandler is None: 
            super().hoverEnterEvent(event)
        else:
            self.eventHandler.itemHoverEnterEvent(event) 

    def hoverLeaveEvent(self, event):

        if self.eventHandler is None: 
            super().hoverLeaveEvent(event)
        else:
            self.eventHandler.itemHoverLeaveEvent(event) 

    def hoverMoveEvent(self, event): 

        if self.eventHandler is None: 
            super().hoverMoveEvent(event)
        else:
            self.eventHandler.itemHoverMoveEvent(event) 

    def mousePressEvent(self, event):

        if self.eventHandler is None: 
            super().mousePressEvent(event)
        else:
            self.eventHandler.itemMousePressEvent(event) 

    def mouseMoveEvent(self, event):

        if self.eventHandler is None: 
            super().mouseMoveEvent(event)
        else:
            self.eventHandler.itemMouseMoveEvent(event) 

    def mouseReleaseEvent(self, event):

        if self.eventHandler is None: 
            super().mouseReleaseEvent(event)
        else:
            self.eventHandler.itemMouseReleaseEvent(event) 

    def wheelEvent(self, event):

        if self.eventHandler is None: 
            super().wheelEvent(event) 
        else:
            self.eventHandler.itemWheelEvent(event) 

    def mouseDoubleClickEvent(self, event):
        
        if self.eventHandler is None:
            super().mouseDoubleClickEvent(event)
        else:
            self.eventHandler.itemMouseDoubleClickEvent(event)


class ImageViewCursor():
    """Base class for ImageView Cursor Tools.
    
    Features
    --------
    Show pixel value: hover over image
    Pan: one-finger mouse move with left button held
    Window: one-finger mouse move with right button held
    Zoom: two-finger up/down or mouse wheel event
    Zoom in: double-click left mouse button
    Zoom out: double-click right mouse button

    Can be subclassed to create tools that edit the mask 
    (e.g. to paint, erase or draw)
    """

    def __init__(self): 

        contrastPixMap = QPixmap(icons.contrast)
        handPointPixMap = QPixmap(icons.hand_point_090)
        arrowMovePixMap = QPixmap(icons.arrow_move)

        self.contrastCursor = QCursor(contrastPixMap, hotX=4, hotY=0)
        self.handPointCursor = QCursor(handPointPixMap, hotX=4, hotY=0)
        self.arrowMoveCursor = QCursor(arrowMovePixMap, hotX=4, hotY=0)

        self.cursor = QCursor(handPointPixMap, hotX=4, hotY=0)
        self.icon = QIcon(handPointPixMap)
        self.toolTip = "Cursor" 
        self.view = None
        self.x = None
        self.y = None

    def setView(self, imageView):
        """Assign an ImageView instance to handle"""

        self.view = imageView
        self.view.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.view.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.item = imageView.imageItem
        self.item.setAcceptHoverEvents(True)
        self.item.setEventHandler(self)

       # self.view.setDragMode(QGraphicsView.ScrollHandDrag)
        #QScroller.grabGesture(self.viewport(), QScroller.LeftMouseButtonGesture)
        #QScroller.grabGesture(self.viewport(), QScroller.TouchGesture)

    def paint(self, painter, option, widget):
        pass
             
    def itemHoverEnterEvent(self, event):
        
        self.x = int(event.pos().x())
        self.y = int(event.pos().y())
        self.item.setCursor(self.cursor)
        self.view.mousePositionMoved.emit()
        
    def itemHoverLeaveEvent(self, event):
        
        self.x = int(event.pos().x())
        self.y = int(event.pos().y())
        self.view.mousePositionMoved.emit()

    def itemHoverMoveEvent(self, event):

        self.x = int(event.pos().x())
        self.y = int(event.pos().y())
        self.view.mousePositionMoved.emit()

    def itemMousePressEvent(self, event):

        self.x = int(event.pos().x())
        self.y = int(event.pos().y())
        button = event.button()
        if button == Qt.LeftButton:
            self.item.setCursor(self.arrowMoveCursor)
        elif button == Qt.RightButton:
            self.item.setCursor(self.contrastCursor)

    def itemMouseReleaseEvent(self, event):

        self.item.setCursor(self.handPointCursor)

    def itemMouseMoveEvent(self, event):

        self.x = int(event.pos().x())
        self.y = int(event.pos().y())
        button = event.buttons()
        if button == Qt.LeftButton:
            self.pan(event)
        elif button == Qt.RightButton:
            self.window(event)

    def itemWheelEvent(self, event):

        if event.delta() < 0:
            zoomFactor = 1.25
        else:
            zoomFactor = 1/1.25
        self.view.scale(zoomFactor, zoomFactor)

    def itemMouseDoubleClickEvent(self, event):
        pass

    def pan(self, event):
        """Pan the image
        
        Note: this can be implemented more easily as
        self.view.setDragMode(QGraphicsView.ScrollHandDrag)
        but reimplemented here to control the cursor and as a template
        """

        distance = event.screenPos() - event.lastScreenPos()
        self.item.blockSignals(True)
        hBar = self.view.horizontalScrollBar()
        vBar = self.view.verticalScrollBar()
        hBar.setValue(hBar.value() - distance.x())
        vBar.setValue(vBar.value() - distance.y())
        self.item.blockSignals(False)

    def window(self, event):
        """Change intensity and contrast"""

        image = self.item.image
        if image is None: return
        distance = event.screenPos() - event.lastScreenPos()
        center = image.WindowCenter
        width = image.WindowWidth
        if float(center / image.Columns) > 0.01:
            step_y = float(center / image.Columns)
        else:
            step_y = 0.01
        if float(width / image.Rows) > 0.01:
            step_x = float(width/ image.Rows)
        else:
            step_x = 0.01
        horizontalDiff = step_y * distance.y()
        verticalDiff = step_x * distance.x()
        newCenter = center + horizontalDiff
        newWidth = width + verticalDiff
        image.WindowCenter = newCenter
        image.WindowWidth = newWidth
#        print(center-width/2, center+width/2)
        self.item._setPixMap()
        self.item.update()
        self.view.imageUpdated.emit()


class ImageViewZoom(ImageViewCursor):
    """Provides zoom/pan/windowing functionality for a MaskOverlay.
    
    Features
    --------
    Keeps track of cursor position and emits a signal when 
    it has changed.
    
    Comes with a zoom and windowing tool: 
    >>> Left click to zoom in.
    >>> Right click to zoom out.
    >>> Left drag to shift image (pan)
    >>> Right drag to change contrast and window.

    MaskOverlay can be subclassed to create tools that edit the mask 
    (e.g. to paint, erase or draw)
    """

    def __init__(self): 
        super().__init__()

        pixMap = QPixmap(icons.magnifier)
        self.magnifierCursor = QCursor(pixMap, hotX=10, hotY=4)
        self.cursor = QCursor(pixMap, hotX=10, hotY=4)
        self.icon = QIcon(pixMap)
        self.toolTip = 'Zoom tool'
        self.x0 = None
        self.y0 = None

    def paint(self, painter, option, widget):

        if self.x0 is not None:
            width = self.x - self.x0
            height = self.y - self.y0
            pen = QPen()
            pen.setColor(QColor(Qt.white))
            pen.setWidth(0)
            painter.setPen(pen)
            painter.drawRect(self.x0, self.y0, width, height)

    def itemMousePressEvent(self, event):

        self.x = int(event.pos().x())
        self.y = int(event.pos().y())
        button = event.button()
        if button == Qt.LeftButton:
            self.x0 = self.x
            self.y0 = self.y

    def itemMouseReleaseEvent(self, event):

        if event.button() == Qt.LeftButton:
            if self.x0 is not None:
                width = self.x - self.x0
                height = self.y - self.y0
                self.view.fitInView(self.x0, self.y0, width, height, Qt.KeepAspectRatio)
        elif event.button() == Qt.RightButton:
            self.view.fitInView(self.item, Qt.KeepAspectRatio)
        self.x0 = None
        self.y0 = None
        self.item.setCursor(self.cursor)
        self.item.update()

    def itemMouseMoveEvent(self, event):

        self.x = int(event.pos().x())
        self.y = int(event.pos().y())
        button = event.buttons()
        if button == Qt.LeftButton:
            self.item.update()

    def itemWheelEvent(self, event):

        super(self.item.__class__, self.item).wheelEvent(event)