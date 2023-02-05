import os
import mne
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QWidget, QComboBox, QPushButton, QFileDialog, QMessageBox, QHBoxLayout, QMainWindow
from MainWindow import Ui_MainWindow
import resource
from Segnale import Segnale


# Classe utilizzata per la scelta del file .fif, se tutto è andato bene passa il controllo alla Main Window
class Finestrai(QWidget):
    def __init__(self):
        super().__init__()
        window_width, window_height = 280, 160
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
        pushButton.setStyleSheet("border-image:url(:/Cartella.png);\n"
                                 "background: transparent;\n"
                                 "")

        pushButton.clicked.connect(self.getFileName)
        layout = QHBoxLayout()
        layout.setGeometry(QtCore.QRect(200, 240, 400, 300))
        layout.addWidget(label)
        layout.addWidget(pushButton)
        self.setLayout(layout)


    """
       Funzione che si occupa di:
       1) Caricare il file in memoria
       2) Passare il file alla mainWindow
       3) Lanciare eventuali eccezioni
    """
    def openFile(self, stringa: str):
        try:
            # Caricamento del segnale in memoria
            Signal = Segnale(stringa)
            #Signal.insert_data(stringa)

            # Apertura seconda finestra
            self.window2 = QtWidgets.QMainWindow()
            self.ui = Ui_MainWindow(True, stringa)
            self.ui.setupUi(self.window2)
            self.ui.InitializePipeline("load.data: ("+stringa+")")
            self.ui.SetSignal(Signal)
            self.window2.show()
            self.ui.label.setText("File caricato correttamente")

        except ValueError as e:
            self.window2 = QtWidgets.QMainWindow()
            self.ui = Ui_MainWindow(False, stringa)
            self.ui.setupUi(self.window2)
            self.window2.show()
            self.ui.label.setText("A tip: "
                                  "all raw files should end with raw.fif, raw_sss.fif, raw_tsss.fif, _meg.fif, _eeg.fif, _ieeg.fif, raw.fif.gz, raw_sss.fif.gz, raw_tsss.fif.gz, _meg.fif.gz, _eeg.fif.gz or _ieeg.fif.gz")
            """
            #Parlane col professore
            
            ecc = ("This filename " + stringa + " does not conform to MNE naming conventions.")
            x = QWidget()
            QMessageBox.critical(x, "Origine file sconosciuta", ecc)
            """

    def getFileName(self):
        # supported read file formats
        supported = {
            ".edf": mne.io.read_raw_edf,
            ".bdf": mne.io.read_raw_bdf,
            ".gdf": mne.io.read_raw_gdf,
            ".vhdr": mne.io.read_raw_brainvision,
            ".fif": mne.io.read_raw_fif,
            ".fif.gz": mne.io.read_raw_fif,
            ".set": mne.io.read_raw_eeglab,
            ".cnt": mne.io.read_raw_cnt,
            ".mff": mne.io.read_raw_egi,
            ".nxe": mne.io.read_raw_eximia,
            ".hdr": mne.io.read_raw_nirx,
            ".snirf": mne.io.read_raw_snirf,
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
            filter='MNE File (*.fif);',
            #  initialFilter='Excel File (*.xlsx *.xls)'
        )
        if response[0] != '':
            self.openFile(response[0])
            self.close()

    def retranslateUi(self, NeuroClean):
        _translate = QtCore.QCoreApplication.translate
        NeuroClean.setWindowTitle(_translate("NeuroClean", "NeuroClean"))
        self.label.setText(_translate("NeuroClean", "Select an .edf or .fif file"))


""""

qlineargradient(spread:pad, x1:0, y1:1, x2:1, y2:0, stop:0.0284091 rgba(194, 0, 183, "
            "255), stop:0.119318 rgba(14, 8, 73, 255), stop:0.409091 rgba(28, 17, 145, 255), stop:0.727273 rgba(126, "
            "14, 81, 255), stop:0.965909 rgba(244, 70, 5, 255), stop:0.977273 rgba(234, 11, 11, 255), stop:1 rgba("
            "255, 136, 0, 255))


"""
