from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout
from callbacks import *
from log_window import *
from list_window import *

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

