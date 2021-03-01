from PyQt5.QtWidgets import QFileDialog, QDialog
from data import *
from image_window import *

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
