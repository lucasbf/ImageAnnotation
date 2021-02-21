import os
import json

from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QPushButton, QAction, QLineEdit, QInputDialog 
from PyQt5.QtWidgets import QMessageBox, QVBoxLayout, QPlainTextEdit, QFileDialog, QDialog, QListWidget, QLabel, QGridLayout
from PyQt5.QtGui import QIcon, QImage, QPixmap, QPainter, QPen
from PyQt5 import QtGui
from PyQt5.QtCore import pyqtSlot, Qt, QPoint, QRect, QItemSelectionModel

class ROIRepo:
    def __init__(self):
        self.__annotations = {}
 
    def insertROI(self,idname,roi):
        if idname in self.__annotations.keys():
            self.__annotations[idname].append(roi)
        else:
            self.__annotations[idname] = [roi]

    def updateROI(self,idname,rois):
        if idname in self.__annotations.keys():
            self.__annotations[idname] = rois

    def getROI(self,idname):
        return self.__annotations[idname] if idname in self.__annotations.keys() else []

    def getROIStr(self,idname):
        return ['({},{},{},{})'.format(r['x1'],r['y1'],r['x2'],r['y2']) for r in self.__annotations[idname]] if idname in self.__annotations.keys() else []

    def loadFromFile(self,path='.'):
        with open('{}/annotation.json'.format(path),'r') as jsonfile:
            self.__annotations = json.load(jsonfile)

    def saveToFile(self,path='.'):
        with open('{}/annotation.json'.format(path),'w') as jsonfile:
            json.dump(self.__annotations,jsonfile,indent=4)

class DataPool:
    __dataPool__ = None

    def __init__(self):
        self.path = None
        self.fileOpened = ''
        self.filenames = None
        self.image = None
        self.drawing = False
        self.ix = 0
        self.iy = 0
        self.ipos = None
        self.lineColor = Qt.red
        self.lineWidth = 3
        self.roiRepo = ROIRepo()
        self.roiclone = False
        self.roiCloned = None

        if DataPool.__dataPool__ is None:
            DataPool.__dataPool__ = self
        else:
            raise Exception("Only one DataPool is allowed")

    @staticmethod
    def getInstance():
        if not DataPool.__dataPool__:
            DataPool()
        return DataPool.__dataPool__

class Callbacks:
    def __init__(self,component):
        self.component = component

    def openFolder(self):
        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.DirectoryOnly)

        if dlg.exec_() == QDialog.Accepted:
            dp = DataPool.getInstance()
            path = dlg.selectedFiles()[0]
            _, _, dp.filenames = next(os.walk(path))
            dp.path = path
            if 'annotation.json' in dp.filenames:
                dp.roiRepo.loadFromFile(path)
                dp.filenames.remove('annotation.json')
            self.component.fileWindow.loadList(dp.filenames)

    def loadImage(self,item):
        dp = DataPool.getInstance()
        if self.component.imageWindow != None:
            self.component.imageWindow.close()

        dp.fileOpened = item if type(item) is str else item.text()
        path = DataPool.getInstance().path
        pf = '{}/{}'.format(path,dp.fileOpened)
        self.component.logWindow.loadInfo('Loading Image {}'.format(pf))
        self.component.imageWindow = ImageWindow(dp.fileOpened,pf,self.component.logWindow,self.imageKeyEvent)

    def imageKeyEvent(self, event):
        dp = DataPool.getInstance()
        idx = dp.filenames.index(dp.fileOpened)
 
        if event.key() == Qt.Key_Down and idx < len(dp.filenames) - 1:
            self.loadImage(dp.filenames[idx+1])
        elif event.key() == Qt.Key_Up and idx > 0:
            self.loadImage(dp.filenames[idx-1])

    def cloneROI(self):
        dp = DataPool.getInstance()
        if self.component.btClone.text() == 'Clone (Stop)':
            self.component.btClone.setText('Clone')
            dp.roiclone = False
            dp.roiCloned = None 
        elif self.component.imageWindow:
            self.component.imageWindow.cloneRoi()
            self.component.btClone.setText('Clone (Stop)')

    def insertCoordinates(self):
        if self.component.imageWindow:
            self.component.btClone.setText('Clone (Stop)')
            self.component.imageWindow.insertRoi()

    def exitApp(self):
        dp = DataPool.getInstance()
        dp.roiRepo.saveToFile(dp.path)
        exit()

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

class LogWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = 'Annotation QT - [Log]'
        self.left = 10
        self.top = 500
        self.width = 800
        self.height = 300
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left,self.top,self.width,self.height)

        self.textbox = QPlainTextEdit(self)
        self.textbox.move(1,1)
        self.textbox.resize(self.width,self.height)
        self.textbox.setReadOnly(True)

    def loadInfo(self,info):
        self.textbox.insertPlainText(info + '\n')

class ListWindow(QMainWindow):
    def __init__(self, title, left=1000, top=10, width=300, height=800):
        super().__init__()
        self.title = title
        self.left = left
        self.top = top
        self.width = width
        self.height = height
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left,self.top,self.width,self.height)

        self.listview = QListWidget(self)
        self.listview.move(1,1)
        self.listview.resize(self.width,self.height)

    def loadList(self,infoList):
        self.listview.clear()
        for info in infoList:
            self.listview.addItem(info)

class MainWindow:
    def __init__(self):
        self.initUI()
        self.imageWindow = None
        self.initCallbacks()

    def initUI(self):
        self.window = QWidget()
        self.layout = QVBoxLayout()

        self.btOpenFolder = QPushButton('Open Folder')
        self.layout.addWidget(self.btOpenFolder)
        self.btClone = QPushButton('Clone')
        self.layout.addWidget(self.btClone)
        self.btInsert = QPushButton('Insert Coord')
        self.layout.addWidget(self.btInsert)
        self.btExit = QPushButton('Exit')
        self.layout.addWidget(self.btExit)

        self.window.setLayout(self.layout)
        self.logWindow = LogWindow()
        self.fileWindow = ListWindow('Files',left=1400)
        self.imageWindow = None

    def initCallbacks(self):
        self.callbacks = Callbacks(self)
        self.btOpenFolder.clicked.connect(self.callbacks.openFolder)
        self.fileWindow.listview.currentItemChanged.connect(self.callbacks.loadImage)
        self.btClone.clicked.connect(self.callbacks.cloneROI)
        self.btInsert.clicked.connect(self.callbacks.insertCoordinates)
        self.btExit.clicked.connect(self.callbacks.exitApp)

    def show(self):
        self.window.show()
        self.logWindow.show()
        self.fileWindow.show()

def main():
    app = QApplication([])
    mainWindow = MainWindow()
    mainWindow.show()
    app.exec()

if __name__ == '__main__':
    main()
