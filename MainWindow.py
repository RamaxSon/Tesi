import numpy
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QComboBox, QListView, QWidget, QMessageBox, QFileDialog
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMainWindow
from mne import channel_type
import os
import inspect #Controllare presenza o meno di window
from Pipeline import Pipeline
from Segnale import Segnale
from Windows.channel import ChannelProperties
from Windows.PipeWindow import PipelineWindow
from Windows.InfoWindow import InfoWindow
from Windows.FilteringSignal import FilterSignal
from Windows.FunctionWindow import FunctionWindow
import importlib


class Ui_MainWindow(QMainWindow):

    def __init__(self):
        self.pipeline = Pipeline()
        self.signal = []
        self.check = False
        self.str = ""
        self.rewrite = False

    def setupUi(self, MainWindow):

        MainWindow.setObjectName("NeuroClean")
        MainWindow.setStyleSheet("background-color:#8C8C8C;")  #7E7E7E variante del colore
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setAutoFillBackground(True)
        self.centralwidget.setObjectName("centralwidget")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setObjectName("label")
        self.label.setStyleSheet("background: transparent;\n"
                                 "font: 75 11pt \"Yu Gothic\";\n"
                                 "color: rgb(255, 255, 255);\n"
                                 "text-align: center;\n"
                                 "")
        self.label.setWordWrap(True)

        # Bottone per modificare la pipeline
        self.pipeButton = QtWidgets.QPushButton(self.centralwidget)
        self.pipeButton.setObjectName("pipeButton")
        self.pipeButton.setGeometry(QtCore.QRect(5, 5, 25, 30))
        self.pipeButton.setToolTip("Modify the pipeline")
        self.pipeButton.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.pipeButton.setStyleSheet("border-image:url(:Icons/edit.png);\n"
                                      "background: transparent; border-radius:10%;\n"
                                      "")
        self.pipeButton.clicked.connect(self.modifyPipeline)

        # Bottone per salvare la pipeline
        self.saveButton = QtWidgets.QPushButton(self.centralwidget)
        self.saveButton.setObjectName("saveButton")
        self.saveButton.setGeometry(QtCore.QRect(45, 5, 25, 30))
        self.saveButton.setToolTip("Save the pipeline")
        self.saveButton.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.saveButton.setStyleSheet("border-image:url(:Icons/save.png);\n"
                                      "background: transparent; border-radius:10%;\n"
                                      "")
        self.saveButton.setShortcut("Ctrl+S")
        self.saveButton.clicked.connect(self.savePipeline)  #PyQt salvare file ecc

        # Bottone per caricare una pipeline già esistente
        self.loadButton = QtWidgets.QPushButton(self.centralwidget)
        self.loadButton.setObjectName("loadButton")
        self.loadButton.setGeometry(QtCore.QRect(85, 5, 25, 30))
        self.loadButton.setToolTip("Load a pipeline")
        self.loadButton.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.loadButton.setStyleSheet("border-image:url(:Icons/upload.png);\n"
                                      "background: transparent; border-radius:10%;\n"
                                      "")
        self.loadButton.setShortcut("Ctrl+S")
        self.loadButton.clicked.connect(self.loadPipeline)

        # Bottone per caricare una pipeline già esistente
        self.infoButton = QtWidgets.QPushButton(self.centralwidget)
        self.infoButton.setObjectName("loadButton")
        self.infoButton.setGeometry(QtCore.QRect(122, 5, 25, 30))
        self.infoButton.setToolTip("Get info about the signal")
        self.infoButton.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.infoButton.setStyleSheet("border-image:url(:Icons/info.png);\n"
                                      "background: transparent; border-radius:10%;\n"
                                      "")
        self.infoButton.setShortcut("Ctrl+I")
        self.infoButton.clicked.connect(self.infoSignal)



        self.label.setGeometry(QtCore.QRect(5, 5, 510, 380))
        MainWindow.resize(589, 390)
        MainWindow.setMinimumSize(589, 390)
        # self.Back.setGeometry(QtCore.QRect(545, 345, 30, 35))

        # Bottone per plottare i sensori/la posizione dei sensori del sengale(?) del segnale.
        self.Plot = QtWidgets.QPushButton(self.centralwidget)
        self.Plot.setGeometry(QtCore.QRect(545, 5, 30, 35))
        self.Plot.setObjectName("Back")
        self.Plot.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.Plot.setStyleSheet("border-image:url(:Icons/blur.png);\n"
                                "background: white; border-radius:5%;\n"
                                "")
        self.Plot.clicked.connect(self.pipeline.plot_locations) # plot location dei segnali
        self.Plot.clicked.connect(self.execPlot)

        # Bottone per plottare la Densità Spettrale di Potenza(psd) del segnale.
        self.Plot = QtWidgets.QPushButton(self.centralwidget)
        self.Plot.setGeometry(QtCore.QRect(545, 45, 30, 35))
        self.Plot.setObjectName("Back")
        self.Plot.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.Plot.setStyleSheet("border-image:url(:Icons/histogram.png);\n"
                                "background: white; border-radius:5%;\n"
                                "")
        self.Plot.clicked.connect(self.pipeline.plot_psd) # plot del PSD, i.e., Densità Spettrale di Potenza
        self.Plot.clicked.connect(self.execPlot)

        # Bottone per plottare i dati grezzi
        self.Plot = QtWidgets.QPushButton(self.centralwidget)
        self.Plot.setGeometry(QtCore.QRect(545, 85, 30, 35))
        self.Plot.setObjectName("Back")
        self.Plot.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.Plot.setStyleSheet("border-image:url(:Icons/raw.png);\n"
                                "background: white; border-radius:10%;\n"
                                "")
        self.Plot.setToolTip("Plot of raw data")
        self.Plot.clicked.connect(self.pipeline.plot_data) # plot dei dati grezzi
        self.Plot.clicked.connect(self.execPlot)

        #(RICORDA: SALVARE PIPELINE.JSON + PIPELINE.PY +SEGNALE.EDF)
        self.operazioni = QComboBox(self.centralwidget)
        view = QListView(self.operazioni)
        self.operazioni.setGeometry(QtCore.QRect(20, 335, 225, 33))  # METTI IN LAYOUT
        self.font = QtGui.QFont()
        self.font.setPointSize(11)
        self.operazioni.setFont(self.font)
        self.operazioni.setObjectName("operazioni")
        self.operazioni.setStyleSheet('QComboBox {\n'
                                      '  background-color: white;\n'
                                      '}')

        view.setFont(self.font)
        view.setStyleSheet("QListView::item {                              \
                                                 background-color: white; }                    \
                                                 QListView::item:selected {                     \
                                                 background-color: blue;                        \
                                                }                                               \
                                                ")
        self.operazioni.setView(view)

        self.applica = QtWidgets.QPushButton(self.centralwidget)
        self.applica.setGeometry(QtCore.QRect(255, 335, 65, 33))
        self.applica.setObjectName("applica")
        self.applica.setFont(self.font)
        self.applica.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.applica.setStyleSheet("background-color: white; font: 75 13pt \"Yu Gothic\";")
        self.applica.clicked.connect(self.clicker)
        self.applica.setText("Add")

        self.run = QtWidgets.QPushButton(self.centralwidget)
        self.run.setGeometry(QtCore.QRect(335, 335, 70, 33))
        self.run.setObjectName("run")
        self.run.setFont(self.font)
        self.run.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.run.setStyleSheet("background-color: white; font: 75 13pt \"Yu Gothic\";")
        self.run.clicked.connect(self.executePipeline)
        self.run.setToolTip("Run/Execute the current Pipeline")
        self.run.setText("Run")

        self.exec = QtWidgets.QPushButton(self.centralwidget)
        self.exec.setGeometry(QtCore.QRect(420, 335, 70, 33))
        self.exec.setObjectName("execute")
        self.exec.setFont(self.font)
        self.exec.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.exec.setStyleSheet("background-color: white; font: 75 13pt \"Yu Gothic\";")
        self.exec.clicked.connect(self.execStep)
        self.exec.setToolTip("Perform the selected step")
        self.exec.setVisible(False)
        self.exec.setText("Exec")

        # Aggiunta step pipeline nel combo box
        path = ("Functions")
        self.dir = []
        for i in os.listdir(path):
            if (i != "__pycache__" and i != "Plot.py" and i != "infoSignal.py"):
                self.dir.append(i.rstrip(".py"))
        for x in self.dir:
            self.operazioni.addItem(x.rstrip(".py"))

        MainWindow.setCentralWidget(self.centralwidget)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("NeuroClean", "NeuroClean"))

    # Cosa ho preso dalla pipeline
    def clickersrt(self):
        x = self.operazioni.currentText()
        if (self.check == True):
            if (x == "Detect automatically the artifacts"):
                pass
            elif (x == "Channel properties"):
                info = self.segnale.return_info()
                X = ChannelProperties(info)
                if X.exec():
                    X.model.sort(0)
                    bads = []
                    renamed = {}
                    types = {}
                    for i in range(X.model.rowCount()):
                        new_label = X.model.item(i, 1).data(Qt.DisplayRole)
                        old_label = info["ch_names"][i]
                        if new_label != old_label:
                            renamed[old_label] = new_label
                        new_type = X.model.item(i, 2).data(Qt.DisplayRole).lower()
                        old_type = channel_type(info, i).lower()
                        if new_type != old_type:
                            types[new_label] = new_type
                        if X.model.item(i, 3).checkState() == Qt.Checked:
                            bads.append(info["ch_names"][i])
                    self.segnale.set_channel_properties(bads)
                    if (self.rewrite):
                        self.pipeline.modify((f"channel_propeties.data.info['bads'] = {bads}"),
                                             {"channel_propeties_bads": bads}, self.indexModify)
                        self.rewrite = False
                    else:
                        self.pipeline.x((f"channel_propeties.data.info['bads'] = {bads}"),
                                        {"channel_propeties_bads": bads})
            elif (x == "Info of the signal"):
                print(self.segnale.return_info())
                self.x = InfoWindow(self.segnale.return_info())
                self.x.show()
                self.label.setText("Complete information about the signal are printed in the terminal")
            elif (x == "View the current pipeline"):
                y = ('\n'.join(map(str, self.pipeline.return_pipeline())))
                Z = PipelineWindow(self.pipeline)
                if Z.exec():
                    self.indexModify = Z.index
                    if (self.indexModify != None):
                        codice = self.pipeline.operations[self.indexModify][0]
                        self.rewrite = True
                        print(codice)
                        if (codice == "load_data"):
                            self.operazioni.setCurrentText("Select an input file")
                            self.clicker()
                        elif (codice == "channel_propeties_bads"):
                            self.operazioni.setCurrentText("Channel properties")
                            self.clicker()
                        elif (codice == "filter"):
                            self.operazioni.setCurrentText("Filtering Signal")
                            self.clicker()
            elif (x == "Filtering Signal"):
                Z = FilterSignal()
                if Z.exec():
                    low = Z.low()
                    high = Z.high()
                    if ((high != None) or (low != None)):
                        z = self.segnale.filtering(low, high)
                        if (z == 1):
                            str1 = f"signal.bandpass.filter = [" + str(low) + " , " + str(high) + "]"
                            # str2 = {"filter" : [low, high]}
                        elif (z == 2):
                            str1 = f"signal.highpass.filter = [" + str(high) + "]"
                            # str2 = ["filter", [low, high]]
                        elif (z == 3):
                            str1 = f"signal.lowpass.filter = [" + str(low) + "]"
                            # str2 = ["filter", [low, high]]
                        str2 = {"filter": [low, high]}

                        if (self.rewrite):
                            self.pipeline.x(str1, str2, self.indexModify, self.rewrite)
                            self.rewrite = False
                        else:
                            self.pipeline.x(str1, str2, 0, self.rewrite)
                            self.rewrite = True

    def clicker(self):
        x = self.operazioni.currentText()
        diz = {}
        for y in self.dir:
            if y == x:
                q = "Functions." + x
                mymodule = importlib.import_module(q)
                check = self.checkWindow(x)  #Utilizzata per controllare se la funzione ha una finestra già implementata

                f = mymodule.Function()

                if check:  #La funzione ha una sua personale finestra °organizza bene questo if sul rewrite
                    if self.rewrite:
                        for key in self.pipeline.pipeline[self.indexModify][x].keys():
                            f.parameters[key]["value"] = self.pipeline.pipeline[self.indexModify][x][key]["value"]
                    window = mymodule.Window(f.parameters)
                    window.setWindowFlags(window.windowFlags() & ~Qt.WindowContextHelpButtonHint)
                    window.setWindowFlags(window.windowFlags() | Qt.WindowMinimizeButtonHint)
                    if window.exec() and window.result():  #window.result() sostituiscilo con segnale reject
                        f.new(window.result())
                        diz[x] = f.parameters
                        if self.rewrite:
                            self.pipeline.x(diz, self.indexModify, self.rewrite)
                            self.rewrite = False
                            self.check = True
                        else:
                            self.pipeline.x(diz, 0, self.rewrite)
                            self.pipeline.imports.append("import "+x)
                            self.check = True
                else:  #Si utilizza la window di default
                    if(self.rewrite):
                        for key in self.pipeline.pipeline[self.indexModify][x].keys():
                            f.parameters[key]["value"] = self.pipeline.pipeline[self.indexModify][x][key]["value"]
                    X = FunctionWindow(f.parameters, x)
                    X.setWindowFlags(X.windowFlags() & ~Qt.WindowContextHelpButtonHint)
                    X.setWindowFlags(X.windowFlags() | Qt.WindowMinimizeButtonHint)
                    if X.exec():
                        f.new(X.result())
                        diz[x] = f.parameters
                        if self.rewrite:
                            self.pipeline.x(diz, self.indexModify, self.rewrite)
                            self.rewrite = False
                            self.check = True
                        else:
                            self.pipeline.x(diz, 0, self.rewrite)
                            self.pipeline.imports.append("import " + x)
                            self.check = True


    # Caricamento nella main window del segnale
    def SetSignal(self, signal: Segnale):
        self.segnale = signal

    def modifyPipeline(self):
        y = ('\n'.join(map(str, self.pipeline.return_pipeline())))
        print(y)
        Z = PipelineWindow(self.pipeline)
        if Z.exec():
            self.pipeline = Z.pipeline
            self.indexModify = Z.index
            if self.indexModify is not None:
                codice = self.pipeline.pipeline[self.indexModify]
                self.rewrite = True
                for j in codice.keys():
                    k = j
                self.operazioni.setCurrentText(k)
                self.clicker()
            else:
                pass

    def savePipeline(self):
        name = QFileDialog.getSaveFileName(caption = "Choose the directory where save your work")
        print(name)
        self.pipeline.save(name[0])

    def loadPipeline(self):
        name = QFileDialog.getOpenFileName(
            caption='Select pipeline',
            directory=os.getcwd(),
            filter='JSON File (*.json);',
            #  initialFilter='Excel File (*.xlsx *.xls)'
        )
        if name[0] != '':
            self.pipeline.load(name[0])

    def executePipeline(self):
        consistent = True
        if len(self.pipeline.pipeline) == 0 or list(self.pipeline.pipeline[0].keys())[0] != "OpenFile":
            consistent = False
            msg = QMessageBox()
            msg.setWindowTitle("Inconsistent Data")
            msg.setText("The first step should be opening a file\n"
                        "Please set OpenFile as the first step")
            msg.setIcon(QMessageBox.Warning)
            x = msg.exec()

        if consistent:
            self.savePipeline()
            for i in range(0, len(self.pipeline.pipeline)):
                key = list(self.pipeline.pipeline[i].keys())[0]
                if key != "plot":
                    q = "Functions." + key
                    mymodule = importlib.import_module(q)
                    if (i == 0):
                        self.signal.append(mymodule.Function().run(self.pipeline.pipeline[i][key]["file"]))
                    else:  # VEDI COSA E COME FARE CON I PLOT
                        if hasattr(mymodule.Function(), "directory"): self.signal.append(mymodule.Function().run(self.pipeline.pipeline[i][key], self.signal[- 1], self.pipeline.directory))
                        else:
                            self.signal.append(mymodule.Function().run(self.pipeline.pipeline[i][key], self.signal[- 1]))
                else:
                    #Definisci per il plot la pipeline di default!!!
                    mymodule = importlib.import_module("Functions.Plot")
                    plot = self.pipeline.pipeline[i]
                    f = mymodule.Function(self.signal[-1], plot["plot"], self.pipeline.directory)
                    f.run()
        if self.signal:
            """Salvataggio del segnale"""
            self.pipeline.addSignal(self.signal)
            self.pipeline.saveSignal()
            self.exec.setVisible(True)

    def execStep(self):
        if self.signal:
            x = self.operazioni.currentText()
            for y in self.dir:
                if y == x:
                    q = "Functions." + x
                    mymodule = importlib.import_module(q)
                    f = mymodule.Function()
                    check = self.checkWindow(x)  #Controlla la presenza o meno della finestra din default per la funzione in escuzione

                    diz = {}
                    if check:  # La funzione ha una sua personale finestra °organizza bene questo if sul rewrite
                        window = mymodule.Window(f.parameters)
                        if window.exec() and window.result():  # window.result() sostituiscilo con segnale reject
                            f.new(window.result())
                            diz[x] = f.parameters
                            self.pipeline.x(diz, 0, self.rewrite)
                            self.pipeline.imports.append("import " + x)
                            self.check = True
                    else:  # Si utilizza la window di default
                        X = FunctionWindow(f.parameters, x)
                        if X.exec():
                            f.new(X.result())
                            diz[x] = f.parameters
                            self.pipeline.x(diz, 0, self.rewrite)
                            self.pipeline.imports.append("import " + x)
                            self.check = True

                    if diz.keys():
                        key = list(diz.keys())[0]
                        if (key == "OpenFile"):
                            self.signal.append(mymodule.Function().run(self.pipeline.pipeline[-1][key]["file"]))
                        else:
                            self.signal.append(
                                mymodule.Function().run(self.pipeline.pipeline[-1][key], self.signal[- 1]))
                    else:
                        pass

    def execPlot(self):
        if self.signal:
            mymodule = importlib.import_module("Functions.Plot")
            plot = self.pipeline.pipeline[-1]
            f = mymodule.Function(self.signal[-1], plot["plot"], self.pipeline.directory)
            f.run()
        else:
           pass

    def checkWindow(self, function : str):
        test = os.path.join("Functions", function + ".py")
        with open(test) as temp_f:
            datafile = temp_f.readlines()
        for line in datafile:
            if 'class Window(QDialog):' in line:
                return True
        return False

    def infoSignal(self):
        if self.signal:
            self.x = InfoWindow(self.signal[-1].info)
            self.x.show()
            self.label.setText("Complete information about the signal are printed in the terminal")
