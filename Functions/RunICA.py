import numpy as np
from mne import preprocessing, io
import picard
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QGridLayout, QLabel, QLineEdit, QDialogButtonBox, QCheckBox, \
    QTreeWidget, QTreeWidgetItem, QPushButton, QMessageBox, QFileDialog
import matplotlib as mpl


class Function:
    """
     Funzione che si occupa di eseguire l'ICA(Independent Component Analysis) sul segnale in ingresso
     ottenendo così le componenti indipendenti del segnale(attraverso matrici di mixing e unmixing),
     potendo utilizzare diversi metodi e definendo più parametri per gestire al meglio le funzionalità del ICA.
    """

    """Definizione parametri della funzione"""

    def __init__(self):
        self.needSignal = False
        self.directory = True
        self.parameters = {"random_state": {"type": "int", "value": None, "default": None},
                           "max_iter": {"type": "int", "value": None, "default": "auto"},
                           "method": {"type": "str", "value": None, "default": "fastica",
                                      "options": ["fastica", "picard", "infomax"],
                                      "others": {"type": "bool", "name": "extends", "value" : False}}}

    """Definisce la directory di default sulla quale andare a salvare i plot delle componenti(oltre agli altri plot, la pipeline, il segnale...)"""

    def defaultDirectory(self, directory):
        mpl.rcParams["savefig.directory"] = directory

    """Imposta i parametri della funzione"""

    def new(self, args):
        for key in args.keys():
            self.parameters[key]["value"] = args[key]["value"]

    """Esecuzione della funzione: \n
           1)Prendere in input il numero di componenti(da una finestra ausiliaria); \n
           2)Calcolare l'ICA sul segnale attraverso il .fit(); \n
           3)Apertura di una seconda finestra ausiliaria, nella quale studiare le componenti e decidere se sono o meno artefatti \n
    """

    def run(self, args, signal: io.read_raw, dir):
        self.new(args)
        self.defaultDirectory(dir)
        self.parameters["n_components"] = {}
        self.parameters["n_components"]["type"] = "float"
        self.parameters["n_components"]["value"] = None
        self.parameters["n_components"]["default"] = None
        self.parameters["n_components"][
            "desc"] = "-Greater than 1 and less than or equal to the number of channels,\n  select number of channels -> int value;\n-Between 0 and 1, Will select the smallest number of components \n  required to explain the cumulative variance of the data greater than n_components -> float value;\n-None --> 0.999999 is the default value for this parameter."
        numC = otherParams(self.parameters, "Fit Params", signal.info["nchan"])
        numC.setWindowFlags(numC.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        numC.setWindowFlags(numC.windowFlags() | Qt.WindowMinimizeButtonHint)
        if numC.exec():
            self.parameters["n_components"]["value"] = numC.result()  # , self.montage
            fit_params = {}
            if self.parameters["method"]["value"] != "picard":
                fit_params["extended"] = self.parameters["method"]["others"]["value"]
            signal.filter(l_freq=1., h_freq=None)  # ICA works best with a highpass filter applied
            if len(fit_params.keys()) > 1:
                ica = preprocessing.ICA(n_components=self.parameters["n_components"]["value"],
                                        method=self.parameters["method"]["value"],
                                        max_iter=self.parameters["max_iter"]["value"],
                                        random_state=self.parameters["random_state"]["value"],
                                        fit_params=fit_params)
            else:
                ica = preprocessing.ICA(n_components=self.parameters["n_components"]["value"],
                                        method=self.parameters["method"]["value"],
                                        max_iter=self.parameters["max_iter"]["value"],
                                        random_state=self.parameters["random_state"]["value"])
            ica.fit(signal)
            componenti = ica.n_components_
            Analysis = ICAAnalysis(ica, signal, "ICA Component Analysis", componenti)
            Analysis.setWindowFlags(Analysis.windowFlags() & ~Qt.WindowContextHelpButtonHint)
            Analysis.setWindowFlags(Analysis.windowFlags() | Qt.WindowMinimizeButtonHint)
            if Analysis.exec():
                if Analysis.excluded is not None:
                    ica.apply(signal, exclude=Analysis.excluded)
            return signal
        else:
            return signal


class otherParams(QDialog):
    """
    Finestra ausiliaria per prendere in input il numero di componenti del segnale:/n
    -Numero intero maggiore di 1 e minore del numero di canali del segnale, oppure\n
    -Numero razionale tra 0 e 1 per indicare la varianza( se 0.7 le componenti maggiori che assieme descrivono il 70% della varianza)\n
    -None o 0 --> le componenti che descrivono il 99,99% della varianza.
    """

    def __init__(self, Parameters: dict, FunctionName: str, limit: int):
        super().__init__()
        self.setWindowTitle(FunctionName)
        self.param = Parameters
        self.checkCheckable = None
        self.limit = limit
        vbox = QVBoxLayout(self)
        grid = QGridLayout()
        self.edit = {}
        self.others = {}
        left = 0
        right = 0
        validator = QDoubleValidator()
        validator.setRange(0, float(self.limit))
        key1 = "n_components"
        grid.addWidget(QLabel(key1), left, right)
        self.edit[key1] = QLineEdit()
        if self.param[key1]["value"] is not None:
            self.edit[key1].setText(self.param[key1]["value"])
        else:
            self.edit[key1].setText(self.param[key1]["default"])
        right += 1
        grid.addWidget(self.edit[key1], left, right)
        right -= 1
        left += 1
        if self.param[key1]["type"] == "float":
            self.edit[key1].setValidator(validator)
        if "desc" in self.param[key1].keys():
            self.edit[key1].setToolTip(self.param[key1]["desc"])
        if self.param["method"]["value"] == "picard":
            pass
        else:
            pass
            label = QLabel("Orthogonality : ")
            grid.addWidget(label, left, right)
            right += 1
            self.ortho = QCheckBox()
            if self.param["method"]["value"] == "infomax":
                self.ortho.setChecked(False)
                grid.addWidget(self.ortho, left, right)
                right -= 1
                left += 1
            elif self.param["method"]["value"] == "fastica":
                self.ortho.setChecked(True)
                grid.addWidget(self.ortho, left, right)
                right -= 1
                left += 1
        vbox.addLayout(grid)
        self.buttonbox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        vbox.addWidget(self.buttonbox)
        self.buttonbox.accepted.connect(self.accept)
        self.buttonbox.rejected.connect(self.reject)
        vbox.addWidget(self.buttonbox)
        vbox.setSizeConstraint(QVBoxLayout.SetFixedSize)

    """Controllo se un valore è numerico"""
    def isNumeric(self, s: str):
        try:
            float(s)
            return True
        except ValueError:
            return False

    """Restituisce il numero di componenti scelte"""
    def result(self):
        if self.isNumeric(self.edit["n_components"].text()):
            if float(self.edit["n_components"].text()) > 1:
                if float(self.edit["n_components"].text()) > self.limit:
                    return None
                else:
                   return int(self.edit["n_components"].text())  # , self.template
            elif float(self.edit["n_components"].text()) > 0:
                return float(self.edit["n_components"].text())  # , self.template
            else:
                return None
        else:
            return None


class ICAAnalysis(QDialog):
    """
    Finestra che esegue il controllo/manipolazione delle componenti, potendo vederle:\n
    1)Nel tempo con il plot sources;\n
    2)Topoplot di tutte le componenti;\n
    3)Proprietà specifiche per quelle selezionate;\n
    4)Poter vedere cosa accade a segnale se le si imposta come artefatti, prima di averlo fatto.
    """

    def __init__(self, ICA: preprocessing.ica, Signal: io.read_raw, FunctionName: str, components: int):
        super().__init__()
        self.excluded = None
        self.setWindowTitle(FunctionName)
        self.ICA = ICA
        self.signal = Signal
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
        self.listwidget.setColumnCount(3)
        self.listwidget.setHeaderLabels(['Item', 'Properties', 'Artifact'])
        for i in range(0, components):
            item = QTreeWidgetItem(self.listwidget)
            if i < 10:
                item.setText(0, "ICA00" + str(i))
            elif i < 100:
                item.setText(0, "ICA0" + str(i))
            else:
                item.setText(0, "ICA" + str(i))
            item.setCheckState(1, QtCore.Qt.Unchecked)
            item.setCheckState(2, QtCore.Qt.Unchecked)
            self.listwidget.addTopLevelItem(item)
        layout.addWidget(self.listwidget)

        self.buttonProperties = QPushButton()
        self.buttonProperties.setToolTip("Select components to see specifically their properties")
        self.buttonProperties.setText("View Properties")
        self.buttonProperties.setStyleSheet(
            "background-color: white; border-color: #f6f6f6; color: black; padding: 6px 12px; \n"
            "text-align: center; text-decoration: none; display: inline-block; font-size: 12px;")
        layout.addWidget(self.buttonProperties)

        self.PlotComponents = QPushButton()
        self.PlotComponents.setToolTip("Plot Components's properties'(this may take a while/multi-window)")
        self.PlotComponents.setText("Plot Components")
        self.PlotComponents.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.PlotComponents.setStyleSheet(
            "background-color: white; border-color: #f6f6f6; color: black; padding: 6px 12px; \n"
            "text-align: center; text-decoration: none; display: inline-block; font-size: 12px;")
        self.PlotComponents.clicked.connect(self.Plot_Components)
        layout.addWidget(self.PlotComponents)

        self.PlotSources = QPushButton()
        self.PlotSources.setToolTip("Plot Sources of the components(this may take a while/multi-window)")
        self.PlotSources.setText("Plot Sources")
        self.PlotSources.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.PlotSources.setStyleSheet(
            "background-color: white; border-color: #f6f6f6; color: black; padding: 6px 12px; \n"
            "text-align: center; text-decoration: none; display: inline-block; font-size: 12px;")
        self.PlotSources.clicked.connect(self.Plot_Sources)
        layout.addWidget(self.PlotSources)

        self.EOGCorrisp = QPushButton()
        self.EOGCorrisp.setToolTip("Find corrispondence in components with EOG")
        self.EOGCorrisp.setText("Find EOG Corrispondence")
        self.EOGCorrisp.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.EOGCorrisp.setStyleSheet(
            "background-color: white; border-color: #f6f6f6; color: black; padding: 6px 12px; \n"
            "text-align: center; text-decoration: none; display: inline-block; font-size: 12px;")
        self.EOGCorrisp.clicked.connect(self.findEOGcorrispondence)
        layout.addWidget(self.EOGCorrisp)

        self.PlotOverlay = QPushButton()
        self.PlotOverlay.setToolTip("Plot the overlay of the signal before and after the cleaning of the possibles "
                                    "artifacts")
        self.PlotOverlay.setText("Plot Overlay")
        self.PlotOverlay.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.PlotOverlay.setStyleSheet(
            "background-color: white; border-color: #f6f6f6; color: black; padding: 6px 12px; \n"
            "text-align: center; text-decoration: none; display: inline-block; font-size: 12px;")
        self.PlotOverlay.clicked.connect(self.Plot_Overlay)
        layout.addWidget(self.PlotOverlay)

        self.buttonbox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addWidget(self.buttonbox)
        self.buttonProperties.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.buttonbox.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.buttonbox.accepted.connect(self.artifacts)
        self.buttonProperties.clicked.connect(self.ICAproperties)
        self.buttonbox.rejected.connect(self.reject)
        layout.setSizeConstraint(QVBoxLayout.SetFixedSize)

    """Funzione per vedere le proprietà delle componenti che sono impostate come checked"""
    def ICAproperties(self):
        indexes = []
        j = False
        for i in range(0, self.listwidget.topLevelItemCount()):
            if self.listwidget.topLevelItem(i).checkState(1) == QtCore.Qt.Checked:
                indexes.append(i)
                j = True
        if not j:
            return
        else:
            try:
                x = self.signal.copy()
                x.drop_channels(self.signal.info["bads"])
                import matplotlib.pyplot as plt
                from math import trunc
                from mne import viz, pick_info
                from mne.time_frequency import psd_array_welch
                for index in indexes:
                    ica_component = self.ICA.get_components()[:, index]
                    fig = plt.figure()
                    gs = fig.add_gridspec(2, 2)
                    ax1 = fig.add_subplot(gs[0, :])
                    ax2 = fig.add_subplot(gs[1, 0])
                    ax3 = fig.add_subplot(gs[1, 1])
                    tempComp = self.ICA.get_sources(self.signal)[index]
                    duration = trunc(len(self.signal)/int(self.signal.info["sfreq"]))
                    n_samp = np.linspace(0, duration, num=len(tempComp[0][0]))
                    viz.plot_topomap(ica_component, x.info, axes=ax3, show=False)
                    ax3.set_title("Topomap")
                    ax1.plot(n_samp, tempComp[0][0], linewidth=1, color='black')
                    ax1.set_title("Andamento temporale della componente ICA"+str(index))
                    ax1.set_xlabel("Time(s)")
                    ax1.set_ylabel("uV")
                    ax1.grid(True)
                    ica_data = ica_component[np.newaxis, :]
                    sfreq = self.signal.info['sfreq']
                    power, frequencies = psd_array_welch(ica_data, sfreq, fmin=0, fmax=sfreq / 2, n_fft=(self.signal.info["nchan"]-len(self.signal.info["bads"])))
                    ax2.plot(frequencies, power[0], linewidth=1)
                    ax2.set_title("Spettro della componente ICA"+str(index))
                    ax2.set_xlabel("Frequencies(Hz)")
                    ax2.set_ylabel("Power Spectral Density uV\u00B2/Hz")
                    ax2.grid(True)
                    fig.tight_layout()
                    plt.show()
            except RuntimeError as e:
                msg = QMessageBox()
                msg.setWindowTitle("Operation denied")
                msg.setText(str(e))
                msg.setIcon(QMessageBox.Warning)
                messageError = msg.exec()

    """Funzione per impostare le componenti che sono checked come artefatti"""
    def findEOGcorrispondence(self):
        try:
            eog_indices, eog_scores = self.ICA.find_bads_eog(self.signal)
            for i in range(0, self.listwidget.topLevelItemCount()):
                if i in eog_indices:
                    item = self.listwidget.topLevelItem(i)
                    item.setCheckState(2, QtCore.Qt.Checked)
            self.ICA.plot_scores(eog_scores)
        except RuntimeError as e:
            msg = QMessageBox()
            msg.setWindowTitle("Operation denied")
            msg.setText(str(e) + " through the mne function")
            msg.setIcon(QMessageBox.Warning)
            messageError = msg.exec()

    """Funzione che si occupa della rimozione degli artefatti"""
    def artifacts(self):
        indexes = []
        j = False
        for i in range(0, self.listwidget.topLevelItemCount()):
            if self.listwidget.topLevelItem(i).checkState(2) == QtCore.Qt.Checked:
                indexes.append(i)
                j = True
        if not j:
            return
        else:
            self.excluded = indexes
            return self.accept()

    """Topoplot di tutte le componenti"""
    def Plot_Components(self):
        try:
            self.ICA.plot_components()
        except RuntimeError as e:
            msg = QMessageBox()
            msg.setWindowTitle("Operation denied")
            msg.setText(str(e))
            msg.setIcon(QMessageBox.Warning)
            messageError = msg.exec()

    """Plot temporale delle componenti"""

    def Plot_Sources(self):
        try:
            self.ICA.plot_sources(self.signal)
        except RuntimeError as e:
            msg = QMessageBox()
            msg.setWindowTitle("Operation denied")
            msg.setText(str(e))
            msg.setIcon(QMessageBox.Warning)
            messageError = msg.exec()

    """Funzione per vedere l'impatto della scelta di alcune componenti(quelle checked) come artefatti"""

    def Plot_Overlay(self):
        indexes = []
        j = False
        for i in range(0, self.listwidget.topLevelItemCount()):
            if self.listwidget.topLevelItem(i).checkState(2) == QtCore.Qt.Checked:
                indexes.append(i)
                j = True
        if not j:
            return
        else:
            try:
                self.ICA.plot_overlay(self.signal, exclude=indexes)
            except RuntimeError as e:
                msg = QMessageBox()
                msg.setWindowTitle("Operation denied")
                msg.setText(str(e))
                msg.setIcon(QMessageBox.Warning)
                messageError = msg.exec()
