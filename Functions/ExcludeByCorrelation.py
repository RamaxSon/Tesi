import mne
from mne_connectivity import envelope_correlation
import numpy as np
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QMessageBox, QDialog, QGridLayout, QTreeWidget, QTreeWidgetItem, QPushButton, \
    QDialogButtonBox


class Function:
    """
    Funzione che .
    """

    """Definizione parametri della funzione"""
    def __init__(self):
        self.needSignal = True
        self.parameters = {"excluded": {"type": "list", "value": None, "default": []}}

    """Imposta i parametri della funzione"""
    def new(self, args):
        self.parameters["excluded"]["value"] = args["excluded"]["value"]

    """Gli step vedi dopo"""
    def run(self, args, signal : mne.io.read_raw):
        self.new(args)
        try:
            if self.parameters["excluded"]["value"] != []:
                signal.info["bads"] = self.parameters["excluded"]["value"]
            return signal
        except ValueError as e:
            msg = QMessageBox()
            msg.setWindowTitle("Operation denied")
            msg.setText(str(e))
            msg.setIcon(QMessageBox.Warning)
            messageError = msg.exec()
            return signal

class Window(QDialog):
    def __init__(self, parameters, signal):
        super().__init__()
        self.setObjectName("ExcludeByCorrelation")
        self.setWindowTitle("Exclude channels by correlation between electrodes")
        self.resize(300, 331)

        self.signal = signal
        self.inspect = []
        self.artifact = []
        layout = QGridLayout()
        self.setLayout(layout)

        self.listwidget = QTreeWidget()
        self.listwidget.setStyleSheet("background-color: #f6f6f6;\n"
                                      "font: 75 11pt \"Yu Gothic\";\n"
                                      "color: black;\n"
                                      "text-align: center;\n"
                                      "")
        self.listwidget.setColumnCount(2)
        self.listwidget.setHeaderLabels(['Electrode', 'Exclude'])
        for i in range(0, int(self.signal.info["nchan"])):
            item = QTreeWidgetItem(self.listwidget)
            item.setText(0, self.signal.info["chs"][i]["ch_name"])
            item.setCheckState(1, QtCore.Qt.Unchecked)
            self.listwidget.addTopLevelItem(item)
        layout.addWidget(self.listwidget)

        self.evaluateCorrelation = QPushButton()
        self.evaluateCorrelation.setToolTip("Select components to see specifically their properties")
        self.evaluateCorrelation.setText("Compute correlation")
        self.evaluateCorrelation.setStyleSheet(
            "background-color: white; border-color: #f6f6f6; color: black; padding: 6px 12px; \n"
            "text-align: center; text-decoration: none; display: inline-block; font-size: 12px;")
        self.evaluateCorrelation.clicked.connect(self.Correlation)
        layout.addWidget(self.evaluateCorrelation)
        self.buttonbox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addWidget(self.buttonbox)
        self.evaluateCorrelation.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.buttonbox.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.buttonbox.accepted.connect(self.result)
        self.buttonbox.rejected.connect(self.reject)

    def Correlation(self):
        duration = 10
        events = mne.make_fixed_length_events(self.signal, duration=10)
        tmax = duration - 1. / self.signal.info['sfreq']
        epochs = mne.Epochs(self.signal, events=events, baseline=None, tmin=0, tmax=tmax)
        corr = envelope_correlation(epochs)
        corr = corr.get_data(output='dense')[:, :, 0]
        threshold = 0.5
        excluded_channels = np.where(corr < threshold, 'excluded', 'included')
        print(excluded_channels)
        #set self.qualcosa[excluded_channels]



    def result(self):
        pass