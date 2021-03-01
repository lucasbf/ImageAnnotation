from PyQt5.QtWidgets import QMainWindow, QListWidget

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
