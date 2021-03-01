from PyQt5.QtWidgets import QMainWindow, QMessageBox, QInputDialog
from PyQt5.QtGui import QImage, QPixmap, QPainter, QPen
from PyQt5.QtCore import Qt, QPoint, QRect

from data import *
from log_window import *
from list_window import *

class ImageWindow(QMainWindow):
    def __init__(self, title, fileimg, logWindow, keyboardEvent = None):
        super().__init__()
        self.image = None
        self.title = title
        self.filename = title
        self.left = 0
        self.top = 0
        self.width = 800
        self.height = 600
        self.fileimg = fileimg
        self.logWindow = logWindow
        self.listRoi = ListWindow('ROIs')
        self.newRect = None
        self.idxRoi = -1
        self.__keyboardEvent = keyboardEvent
        self.initUI()
        self.initData()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.image = QPixmap(self.fileimg)
        self.setGeometry(self.left,self.top,self.image.width(),self.image.height())
        self.listRoi.listview.currentItemChanged.connect(self.selectROI)
        self.listRoi.listview.keyPressEvent = self.keyPressROI
        self.listRoi.show()
        self.show()

    def initData(self):
        self.__loadROI()

    def __loadROI(self):
        dp = DataPool.getInstance()
        rois = dp.roiRepo.getROIStr(self.title)
        self.listRoi.loadList(rois)

    def __drawROI(self,painter):
        dp = DataPool.getInstance()
        rois = dp.roiRepo.getROI(dp.fileOpened)
        for i,roi in enumerate(rois):
            if self.idxRoi > -1 and self.idxRoi == i:
                painter.setPen(QPen(Qt.green,dp.lineWidth,Qt.SolidLine))
            else:
                painter.setPen(QPen(dp.lineColor,dp.lineWidth,Qt.SolidLine))
            painter.drawRect(QRect(QPoint(roi['x1'],roi['y1']),QPoint(roi['x2'],roi['y2'])))

    def __roiFromCenter(self,roi,x,y):
        width = roi['x2'] - roi['x1']
        height = roi['y2'] - roi['y1']
        return {'x1': x-width//2, 'y1': y-height//2, 'x2': x+width//2, 'y2': y+height//2 }

    def selectROI(self):
        painter = QPainter(self.image)
        painter.drawPixmap(self.rect(),self.image)
        self.idxRoi = self.listRoi.listview.currentRow()
        self.__drawROI(painter)
        self.update()

    def cloneRoi(self):
        dp = DataPool.getInstance()
        self.idxRoi = self.listRoi.listview.currentRow()
        dp.roiclone = True
        rois = dp.roiRepo.getROI(self.filename)
        if rois != []:
            dp.roiCloned = rois[self.idxRoi] if self.idxRoi > -1 else rois[-1]
            self.logWindow.loadInfo('ROI - CLONED ({},{},{},{})'.format(dp.roiCloned['x1'],dp.roiCloned['y1'],dp.roiCloned['x2'],dp.roiCloned['y2']))

    def insertRoi(self):
        dp = DataPool.getInstance()
        text, ok = QInputDialog.getText(self, 'Input ROI', '(x1,y1,x2,y2):')
        if ok:
            dp.roiclone = True
            coords = [int(v) for v in text.split(',')]
            dp.roiCloned = {'x1': coords[0], 'y1': coords[1], 'x2': coords[2], 'y2': coords[3]}
            self.logWindow.loadInfo('ROI - REGISTRED ({},{},{},{})'.format(dp.roiCloned['x1'],dp.roiCloned['y1'],dp.roiCloned['x2'],dp.roiCloned['y2']))

    def keyPressROI(self, event):
        if event.key()  == Qt.Key_Delete and QMessageBox.question(self, 'Atention', "Do you want to delete selected ROI?", QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            idx = self.listRoi.listview.currentRow()
            dp = DataPool.getInstance()
            rois = dp.roiRepo.getROI(dp.fileOpened)
            rois.pop(idx)
            dp.roiRepo.updateROI(dp.fileOpened,rois)
            self.__loadROI()
            self.update()
        return QListWidget.keyPressEvent(self.listRoi.listview, event)

    def keyPressEvent(self, event):
        if self.__keyboardEvent != None:
            self.__keyboardEvent(event)

    def paintEvent(self, event):
        dp = DataPool.getInstance()
        self.image = QPixmap(self.fileimg)
        painter = QPainter(self)
        painter.drawPixmap(self.rect(),self.image)
        self.__drawROI(painter)
        if self.newRect != None:
            painter.setPen(QPen(dp.lineColor,dp.lineWidth,Qt.SolidLine))
            painter.drawRect(self.newRect)

    def mousePressEvent(self, event):
        dp = DataPool.getInstance()
        if event.button() == Qt.LeftButton and not dp.drawing:
            dp.drawing = True
            if dp.roiclone == True:
                roi = self.__roiFromCenter(dp.roiCloned,event.pos().x(),event.pos().y())
                self.newRect = QRect(QPoint(roi['x1'],roi['y1']),QPoint(roi['x2'],roi['y2']))
            else:
                dp.ipos = event.pos()
                self.setWindowTitle('{} - ({},{})'.format(self.title,dp.ipos.x(),dp.ipos.y()))
                self.logWindow.loadInfo('ROI - INIT Point ({},{})'.format(dp.ipos.x(),dp.ipos.y()))

    def mouseMoveEvent(self, event):
        dp = DataPool.getInstance()
        if dp.drawing == True:
            if dp.roiclone == True:
                roi = self.__roiFromCenter(dp.roiCloned,event.pos().x(),event.pos().y())
                self.newRect = QRect(QPoint(roi['x1'],roi['y1']),QPoint(roi['x2'],roi['y2']))
            else:
                self.newRect = QRect(dp.ipos,event.pos())
            self.setWindowTitle('{} - ({},{})'.format(self.title,event.pos().x(),event.pos().y()))
            self.update()

    def mouseReleaseEvent(self, event):
        dp = DataPool.getInstance()
        if event.button() == Qt.LeftButton and dp.drawing:
            dp.drawing = False
            if dp.roiclone == True:
                roi = self.__roiFromCenter(dp.roiCloned,event.pos().x(),event.pos().y())
                dp.roiRepo.insertROI(self.filename,roi)
            else:
                self.logWindow.loadInfo('ROI - END Point ({},{})'.format(event.pos().x(),event.pos().y()))
                x1 = min(dp.ipos.x(),event.pos().x())
                x2 = max(dp.ipos.x(),event.pos().x())
                y1 = min(dp.ipos.y(),event.pos().y())
                y2 = max(dp.ipos.y(),event.pos().y())
                dp.roiRepo.insertROI(self.filename,{'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2})
            self.newRect = None
            self.setWindowTitle(self.title)
            self.__loadROI()

    def closeEvent(self, event):
        dp = DataPool.getInstance()
        dp.roiRepo.saveToFile(dp.path)
