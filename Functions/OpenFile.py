import os
import mne
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QWidget, QPushButton, QFileDialog, QMessageBox, QHBoxLayout, QDialog
import resource
from Segnale import Segnale

class Function:
    def __init__(self):
        self.parameters = { "file" : { "type" : "str" , "value" : None}}
        self.self = True

    def new(self, result : dict):
        self.parameters["file"]["value"] = result["value"]

    def run(self, result):
        self.new(result)
        raw = mne.io.read_raw(self.parameters["file"]["value"], preload=True)
        raw.crop(0, 60).load_data()
        return raw


class Window(QDialog):
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

        def openFile(self, stringa: str):
            try:
                # Caricamento del segnale in memoria
                #self.Signal = Segnale(stringa)
                raw = mne.io.read_raw(stringa, preload=True)
                raw.crop(0, 1).load_data()
                self.file = stringa
                self.accept()
            except ValueError as e:
                ecc = ("This filename " + stringa + " does not conform to MNE naming conventions.")
                x = QWidget()
                QMessageBox.critical(x, "Origine file sconosciuta", ecc)
                self.reject()

        def getFileName(self):
            # supported read file formats
            supported = {
                ".edf": mne.io.read_raw_edf,
                ".bdf": mne.io.read_raw_bdf,
                ".gdf": mne.io.read_raw_gdf,
                # ".vhdr": mne.io.read_raw_brainvision,
                ".fif": mne.io.read_raw_fif,
                ".fif.gz": mne.io.read_raw_fif,
                # ".set": mne.io.read_raw_eeglab,
                # ".cnt": mne.io.read_raw_cnt,
                # ".mff": mne.io.read_raw_egi,
                # ".nxe": mne.io.read_raw_eximia,
                # ".hdr": mne.io.read_raw_nirx,
                # ".snirf": mne.io.read_raw_snirf,
                #  ".xdf": read_raw_xdf,
                # ".xdfz": read_raw_xdf,
                # ".xdf.gz": read_raw_xdf,
                # ".mat": read_raw_mat,
            }

            file_filter = 'Data File (*.xlsx *.csv *.dat);; Excel File (*.xlsx *.xls)'
            response = QFileDialog.getOpenFileName(
                parent=self,
                caption='Select a data file',
                directory=os.getcwd(),
                #filter='MNE File (*.fif);',
                #  initialFilter='Excel File (*.xlsx *.xls)'
            )
            if response[0] != '':
                self.openFile(response[0])
                self.exit = {"load_data": response[0]}
                self.close()

        def retranslateUi(self, NeuroClean):
            _translate = QtCore.QCoreApplication.translate
            NeuroClean.setWindowTitle(_translate("NeuroClean", "NeuroClean"))
            self.label.setText(_translate("NeuroClean", "Select an .edf or .fif file"))

        def result(self):
            x = {}
            x["value"] = self.file
            return x





