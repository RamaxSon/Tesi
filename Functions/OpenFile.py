import os
import mne
import numpy
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QWidget, QPushButton, QFileDialog, QMessageBox, QHBoxLayout, QDialog, QVBoxLayout, \
    QDialogButtonBox, QGridLayout, QLabel
import resource


class Function:
    """Funzione per prendere in input un segnale"""

    def __init__(self):
        self.parameters = {"file": {"type": "str", "value": None}}
        self.self = True

    def new(self, result: dict):
        self.parameters["file"]["value"] = result["value"]

    def openMontageOwn(self, File: str, raw):
        import pandas as pd
        df = pd.read_csv(File)
        Electrodes = df['Electrode'].to_list()
        x = df['x'].to_list()
        y = df['y'].to_list()
        z = df['z'].to_list()
        ch_pos = {}
        for i in range(0, raw.info["nchan"]):
            for el in Electrodes:
                el = str(el)
                if "(" in el:
                    elsempio = el.replace(" ","")
                    arr = elsempio.split("(")
                    el1 = arr[0]
                    el2 = arr[1].rstrip(")")
                    if raw.info["chs"][i]["ch_name"].rstrip(".").rstrip(".") == el1:
                        index = Electrodes.index(el)
                        k = raw.info["chs"][i]["ch_name"]
                        ch_pos[k] = [x[index]/1000, y[index]/1000, z[index]/1000]
                    elif raw.info["chs"][i]["ch_name"].rstrip(".").rstrip(".") == el2:
                        index = Electrodes.index(el)
                        k = raw.info["chs"][i]["ch_name"]
                        ch_pos[k] = [x[index]/1000, y[index]/1000, z[index]/1000]
                else:
                    if raw.info["chs"][i]["ch_name"].rstrip(".").rstrip(".") == el:
                        index = Electrodes.index(el)
                        k = raw.info["chs"][i]["ch_name"]
                        ch_pos[k] = [x[index]/1000, y[index]/1000, z[index]/1000]
        index = Electrodes.index("Nz")
        data = mne.utils.Bunch(
            nasion=[x[index]/1000, y[index]/1000, z[index]/1000],
            lpa=ch_pos['T9..'],
            rpa=ch_pos['T10.'],
            ch_pos=ch_pos,
            coord_frame='unknown',
            hsp=None, hpi=None,
        )
        x = mne.channels.make_dig_montage(**data)
        raw.set_montage(x)
        print(x)
        return raw

    def run(self, result):
        self.new(result)
        raw = mne.io.read_raw(self.parameters["file"]["value"], preload=True)
        raw.crop(0, 60).load_data()
        from math import isnan
        montage = True
        for k in raw.info["chs"]:
            if isnan(k["loc"][0]):
                montage = False
        if not montage:  # Fai a caricamento signal per 3D e 2D
            path = ("Montages")
            for x in os.listdir(path):
                if x != "__pycache__":
                    if int(raw.info["nchan"]) == int(x.rstrip("chs.csv")):
                        raw = self.openMontageOwn(path+"/"+x, raw)
        return raw


class Window(QDialog):
    """Finestra per gestire l'input del segnale + controllo che il file scelto sia adatto"""

    def __init__(self, nothing):
        super().__init__()
        self.file = None
        self.qt = "QDialog"

        self.setMinimumSize(280, 160)
        self.setStyleSheet("background-color:qlineargradient(spread:pad, x1:0, y1:1, x2:1, y2:0, stop:0.0284091 "
                           "rgba(194, 0, 183, 255), stop:0.119318 rgba(14, 8, 73, 255), stop:0.409091 rgba(28, "
                           "17, 145, 255), stop:0.727273 rgba(126,14, 81, 255), stop:0.965909 rgba(244, 70, 5, "
                           "255), stop:0.977273 rgba(234, 11, 11, 255), stop:1 rgba(255, 136, 0, 255));")
        label = QtWidgets.QLabel(self)
        label.setGeometry(QtCore.QRect(150, 10, 201, 31))
        label.setStyleSheet("background: transparent;\n"
                            "font: 75 11pt \"Yu Gothic\";\n"
                            "color: rgb(255, 255, 255);\n"
                            "text-align: center;\n"
                            "")

        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("NeuroClean", "NeuroClean"))
        label.setText(_translate("NeuroClean", "Select an EEG signal file "))

        # Bottone per selezionare file dal folder
        pushButton = QPushButton()
        pushButton.setMaximumSize(QtCore.QSize(80, 70))
        pushButton.setGeometry(QtCore.QRect(140, 40, 150, 140))
        pushButton.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        pushButton.setMouseTracking(True)
        pushButton.setStyleSheet("border-image:url(:Icons/Cartella.png);\n"
                                 "background: transparent;\n"
                                 "")

        pushButton.clicked.connect(self.getFileName)
        layout = QHBoxLayout()
        layout.setGeometry(QtCore.QRect(200, 240, 400, 300))
        layout.addWidget(label)
        layout.addWidget(pushButton)
        self.setLayout(layout)

    """Funzione che preleva il file + controllo che sia il formato adatto"""

    def openFile(self, stringa: str):
        try:
            from math import isnan
            self.raw = mne.io.read_raw(stringa, preload=True)
            self.raw.crop(0, 1).load_data()
            self.file = stringa
            self.accept()
        except ValueError as e:
            ecc = ("This filename " + stringa + " does not conform to MNE naming conventions.")
            x = QWidget()
            QMessageBox.critical(x, "Origine file sconosciuta", ecc)
            self.reject()

    def getFileName(self):
        response = QFileDialog.getOpenFileName(
            parent=self,
            caption='Select a data file',
            directory=os.getcwd(),
        )
        if response[0] != '':
            self.openFile(response[0])
            self.exit = {"load_data": response[0]}
            self.close()

    def retranslateUi(self, NeuroClean):
        _translate = QtCore.QCoreApplication.translate
        NeuroClean.setWindowTitle(_translate("NeuroClean", "NeuroClean"))

    """Restituzione parameter leggibile per la pipeline"""

    def result(self):
        x = {"value": self.file}
        return x

    class otherParams(QDialog):
        """Finestra ausiliaria per prendere in input il template del montaggio degli elettrodi"""

        def __init__(self, Parameters: dict, FunctionName: str, limit: int):
            super().__init__()
            self.setWindowTitle(FunctionName)
            self.param = Parameters
            self.checkCheckable = None
            vbox = QVBoxLayout(self)
            grid = QGridLayout()
            self.edit = {}
            self.others = {}
            left = 0
            right = 0
            templateLabel = QLabel("Template")
            grid.addWidget(templateLabel, left, right)
            right += 1
            self.template = QPushButton()
            self.template.clicked.connect(self.inputTemplate)
            grid.addWidget(self.template, left, right)
            right -= 1
            left += 1

            vbox.addLayout(grid)
            self.buttonbox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            vbox.addWidget(self.buttonbox)
            self.buttonbox.accepted.connect(self.accept)
            self.buttonbox.rejected.connect(self.reject)
            vbox.addWidget(self.buttonbox)
            vbox.setSizeConstraint(QVBoxLayout.SetFixedSize)

        def inputTemplate(self):
            import os
            response = QFileDialog.getOpenFileName(
                parent=self,
                caption='Select a template for montage',
                directory=os.getcwd(),
            )
            if response[0] != '':
                self.template.setText(response[0])
