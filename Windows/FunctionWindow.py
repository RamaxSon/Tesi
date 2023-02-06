from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QGridLayout, QLabel, QLineEdit, QDialogButtonBox, QWidget, QComboBox, \
    QCheckBox


class FunctionWindow(QDialog):
    def __init__(self, Parameters: dict, FunctionName: str):
        super().__init__()
        self.setWindowTitle(FunctionName)  # Ricordati di eliminare filter
        self.param = Parameters
        self.checkCheckable = None
        vbox = QVBoxLayout(self)
        grid = QGridLayout()
        self.edit = {}
        self.others = {}
        left = 0
        right = 0
        onlyInt = QIntValidator()
        onlyInt.setRange(0, 400)
        for key in self.param.keys():
            grid.addWidget(QLabel(key), left, right)
            self.edit[key] = QLineEdit()
            if ("options" in self.param[key].keys()):
                self.edit[key] = QComboBox()
                self.edit[key].addItems(self.param[key]["options"])
                self.edit[key].setCurrentIndex(0)
                if("others" in self.param[key].keys()):
                    self.checkCheckable = 12
                    self.others[key] = self.param[key]["others"]
            elif(self.param[key]["value"] != None):
                self.edit[key].setText(str(self.param[key]["value"]))
            else:
                self.edit[key].setText(self.param[key]["default"])
            right += 1
            grid.addWidget(self.edit[key], left, right)
            right -= 1
            left += 1
            if(self.checkCheckable is not None):
                self.checkCheckable = None
                if (self.others[key]["type"] == "bool"):
                    label = QLabel(list(self.others[key].keys())[1])

                    grid.addWidget(label, left, right)
                    right += 1
                    self.others[key]["value"] = QCheckBox()
                    self.others[key]["value"].setChecked(False)
                    grid.addWidget(self.others[key]["value"], left, right)
                    right -= 1
                    left += 1
            if (self.param[key]["type"] == "int"):  # Per str(QregExp) e float(QDouble) aspetta
                self.edit[key].setValidator(onlyInt)
            if ("desc" in self.param[key].keys()):
                self.edit[key].setToolTip(self.param[key]["desc"])


        vbox.addLayout(grid)
        self.buttonbox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        vbox.addWidget(self.buttonbox)
        self.buttonbox.accepted.connect(self.accept)
        self.buttonbox.rejected.connect(self.reject)
        vbox.addWidget(self.buttonbox)
        vbox.setSizeConstraint(QVBoxLayout.SetFixedSize)

    def result(self):
        x = {}
        for key in self.param.keys():
            if ("options" in self.param[key].keys()):
                x[key] = {"type": self.param[key]["type"], "value": self.edit[key].currentText()}
                if ("others" in self.param[key].keys()):
                    type = self.others[key]["type"]
                    if type == "bool":
                        x[key]["others"] = self.others[key]
                        if(self.others[key]["value"].isChecked()):
                            x[key]["others"]["extends"] = True
                            x[key]["others"].pop("value")
                        else:
                            x[key]["others"]["extends"] = False
                            x[key]["others"].pop("value")
            elif(str(self.edit[key].text()) != ""):
               x[key] ={"type" : self.param[key]["type"], "value" : self.edit[key].text()}
               if (x[key]["type"] == "int" and x[key]["value"].isdigit()):
                   x[key]["value"] = int(x[key]["value"])
            else:
                x[key] = {"type": self.param[key]["type"], "value": self.param[key]["default"]}
               # if(x[key]["value"]):
                #    x[key]["value"] = None
        return x
