import os
import json
from PyQt5.QtCore import Qt

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
