from PyQt5.QtWidgets import QMainWindow, QPlainTextEdit

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
