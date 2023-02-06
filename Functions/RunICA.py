import mne
import picard
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QGridLayout, QLabel, QLineEdit, QDialogButtonBox, QCheckBox, \
     QTreeWidget, QTreeWidgetItem, QPushButton
import matplotlib as mpl

"""
 ICA is sensitive to low-frequency drifts and therefore 
 requires the data to be high-pass filtered prior to fitting.
 Typically, a cutoff frequency of 1 Hz is recommended.
"""

class Function:

    def __init__(self):
        self.directory = True
        self.parameters = {  # "noise_cov": {"type": "Covariance", "value": None, "default": None}}
            "random_state": {"type": "int", "value": None, "default": None},
            "max_iter": {"type": "int", "value": None, "default": "auto"},
            "method": {"type": "str", "value": None, "default": "fastica", "options": ["fastica", "picard", "infomax"],
                       "others": {"type": "bool", "extends": False}}}

    def directorys(self, directory):
        mpl.rcParams["savefig.directory"] = directory

    def new(self, args):
        for key in args.keys():
            self.parameters[key]["value"] = args[key]["value"]

    def run(self, args, signal: mne.io.read_raw, dir):
        self.new(args)
        self.directorys(dir)
        self.parameters["n_components"] = {}
        self.parameters["n_components"]["type"] = "float"
        self.parameters["n_components"]["value"] = None
        self.parameters["n_components"]["default"] = None
        self.parameters["n_components"]["desc"] = "-Greater than 1 and less than or equal to the number of channels,\n  select number of channels -> int value;\n-Between 0 and 1, Will select the smallest number of components \n  required to explain the cumulative variance of the data greater than n_components -> float value;\n-None --> 0.999999 is the default value for this parameter."
        numC = numComp(self.parameters, "Fit Params", signal.info["nchan"])
        numC.setWindowFlags(numC.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        numC.setWindowFlags(numC.windowFlags() | Qt.WindowMinimizeButtonHint)
        if numC.exec():
            self.parameters["n_components"]["value"] = numC.result()
            fit_params = {}
            if self.parameters["method"]["value"] != "picard":
                fit_params["extended"] = self.parameters["method"]["others"]["extends"]
            signal.filter(l_freq=1., h_freq=None)  # ICA works best with a highpass filter applied
            if len(fit_params.keys()) > 1:
                ica = mne.preprocessing.ICA(n_components=self.parameters["n_components"]["value"],
                                            method=self.parameters["method"]["value"],
                                            max_iter=self.parameters["max_iter"]["value"],
                                            random_state=self.parameters["random_state"]["value"],
                                            fit_params=fit_params)
            else:
                ica = mne.preprocessing.ICA(n_components=self.parameters["n_components"]["value"],
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
            return signal #Nessuna Modifica


class numComp(QDialog):
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
        validator = QDoubleValidator()  #Float validator
        validator.setRange(0, limit)
        key = "n_components"
        grid.addWidget(QLabel(key), left, right)
        self.edit[key] = QLineEdit()
        if self.param[key]["value"] != None:
            self.edit[key].setText(self.param[key]["value"])
        else:
            self.edit[key].setText(self.param[key]["default"])
        right += 1
        grid.addWidget(self.edit[key], left, right)
        right -= 1
        left += 1
        if self.param[key]["type"] == "int":  # Per str(QregExp) e float(QDouble) aspetta
            self.edit[key].setValidator(validator)
        if "desc" in self.param[key].keys():
            self.edit[key].setToolTip(self.param[key]["desc"])
        if (self.param["method"]["value"] == "picard"):
            pass
        else:
            pass
            label = QLabel("Orthogonality : ")
            grid.addWidget(label, left, right)
            right += 1
            self.ortho = QCheckBox()
            if (self.param["method"]["value"] == "infomax"):
                self.ortho.setChecked(False)
                grid.addWidget(self.ortho, left, right)
                right -= 1
                left += 1
            elif (self.param["method"]["value"] == "fastica"):
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

    def isNumeric(self, s: str):
        try:
            float(s)
            return True
        except ValueError:
            return False

    def result(self):
        if self.isNumeric(self.edit["n_components"].text()):
            if float(self.edit["n_components"].text()) > 1:
                return int(self.edit["n_components"].text())
            elif float(self.edit["n_components"].text()) > 0:
                return float(self.edit["n_components"].text())
            else:
                return None
        else:
            return None


class ICAAnalysis(QDialog):

    def __init__(self, ICA, Signal: mne.io.read_raw, FunctionName: str, components: int):
        super().__init__()
        self.excluded = None
        self.setWindowTitle(FunctionName)
        self.ICA = ICA
        self.signal = Signal
        #self.setStyleSheet("background-color:#EFEFEF")
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
            if i<10:
                item.setText(0, "ICA00"+str(i))
            elif i<100:
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
            self.ICA.plot_properties(self.signal, picks=indexes, log_scale=True)

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

    def Plot_Components(self):
        self.ICA.plot_components()

    def Plot_Sources(self):
        self.ICA.plot_sources(self.signal)

    def Plot_Overlay(self):
        indexes = []
        j = False
        for i in range(0, self.listwidget.topLevelItemCount()):
            if self.listwidget.topLevelItem(i).checkState(2) == QtCore.Qt.Checked:
                indexes.append(i)
                j = True
        if not j: return
        else:
            self.ICA.plot_overlay(self.signal, exclude=indexes)
