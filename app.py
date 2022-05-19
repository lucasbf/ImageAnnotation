from PyQt5.QtWidgets import QApplication
from main_window import *
 
def main():
    app = QApplication([])
    mainWindow = MainWindow()
    mainWindow.show()
    app.exec_()

if __name__ == '__main__':
    main()
