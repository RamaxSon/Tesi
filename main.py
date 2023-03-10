import sys
from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow
from MainWindow import Ui_MainWindow
import resource


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon('Icons/brain.png'))
    main = QMainWindow()
    myApp = Ui_MainWindow()
    myApp.setupUi(main)
    main.show()

    try:
        sys.exit(app.exec_())
    except SystemExit:
        print('Closing Window...')



