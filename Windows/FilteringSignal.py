from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QGridLayout, QLabel, QLineEdit, QDialogButtonBox, QWidget


class FilterSignal(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Filter Signal")
        vbox = QVBoxLayout(self)
        grid = QGridLayout()
        grid.addWidget(QLabel("low pass filter (Hz):"), 0, 0)
        self.lowedit = QLineEdit()
        grid.addWidget(self.lowedit, 0, 1)
        grid.addWidget(QLabel("high pass filter (Hz):"), 1, 0)
        self.highedit = QLineEdit()
        grid.addWidget(self.highedit, 1, 1)

        onlyInt = QIntValidator()
        onlyInt.setRange(0, 400)
        self.lowedit.setValidator(onlyInt)
        self.highedit.setValidator(onlyInt)

        vbox.addLayout(grid)
        self.buttonbox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        vbox.addWidget(self.buttonbox)
        self.buttonbox.accepted.connect(self.accept)
        self.buttonbox.rejected.connect(self.reject)
        vbox.addWidget(self.buttonbox)
        vbox.setSizeConstraint(QVBoxLayout.SetFixedSize)


    def low(self):
        low = self.lowedit.text()
        return float(low) if low else None

    def high(self):
        high = self.highedit.text()
        return float(high) if high else None