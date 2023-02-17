from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QComboBox, QListView, QMessageBox, QFileDialog
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMainWindow
import os
from Pipeline import Pipeline
from Windows.PipeWindow import PipelineWindow
from Windows.InfoWindow import InfoWindow
from Windows.FunctionWindow import FunctionWindow
import importlib


class Ui_MainWindow(QMainWindow):

    def __init__(self):
        self.pipeline = Pipeline()
        self.signal = []
        self.check = False
        self.rewrite = False

    def setupUi(self, MainWindow):

        MainWindow.setObjectName("NeuroClean")
        MainWindow.setStyleSheet("background-color:#8C8C8C;")  # 7E7E7E variante del colore
        MainWindow.setWindowFlags(MainWindow.windowFlags() & ~Qt.WindowMaximizeButtonHint)
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
        self.saveButton.clicked.connect(self.savePipeline)  # PyQt salvare file ecc

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

        # Bottone per vedere informazioni dettagliate sul segnale
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

        # Bottone per eseguire il plot dei sensori/la posizione+stato dei sensori sullo scalpo.
        self.Plot = QtWidgets.QPushButton(self.centralwidget)
        self.Plot.setGeometry(QtCore.QRect(545, 5, 30, 35))
        self.Plot.setObjectName("Back")
        self.Plot.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.Plot.setStyleSheet("border-image:url(:Icons/blur.png);\n"
                                "background: white; border-radius:5%;\n"
                                "")
        self.Plot.clicked.connect(self.pipeline.plot_locations)  # plot location dei segnali
        self.Plot.clicked.connect(self.execPlot)

        # Bottone per vedere il plot della Densità Spettrale di Potenza(psd) del segnale, i.e., in frequenza.
        self.Plot = QtWidgets.QPushButton(self.centralwidget)
        self.Plot.setGeometry(QtCore.QRect(545, 45, 30, 35))
        self.Plot.setObjectName("Back")
        self.Plot.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.Plot.setStyleSheet("border-image:url(:Icons/histogram.png);\n"
                                "background: white; border-radius:5%;\n"
                                "")
        self.Plot.clicked.connect(self.pipeline.plot_psd)  # plot del PSD, i.e., Densità Spettrale di Potenza
        self.Plot.clicked.connect(self.execPlot)

        # Bottone per vedere il plot dei dati grezzi, i.e., nel tempo.
        self.Plot = QtWidgets.QPushButton(self.centralwidget)
        self.Plot.setGeometry(QtCore.QRect(545, 85, 30, 35))
        self.Plot.setObjectName("Back")
        self.Plot.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.Plot.setStyleSheet("border-image:url(:Icons/raw.png);\n"
                                "background: white; border-radius:10%;\n"
                                "")
        self.Plot.setToolTip("Plot of raw data")
        self.Plot.clicked.connect(self.pipeline.plot_data)  # plot dei dati grezzi
        self.Plot.clicked.connect(self.execPlot)

        self.operazioni = QComboBox(self.centralwidget)
        view = QListView(self.operazioni)
        self.operazioni.setGeometry(QtCore.QRect(20, 335, 225, 33))
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

        #Aggiungere step alla pipeline
        self.applica = QtWidgets.QPushButton(self.centralwidget)
        self.applica.setGeometry(QtCore.QRect(255, 335, 65, 33))
        self.applica.setObjectName("applica")
        self.applica.setFont(self.font)
        self.applica.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.applica.setStyleSheet("background-color: white; font: 75 13pt \"Yu Gothic\";")
        self.applica.clicked.connect(self.clicker)
        self.applica.setText("Add")
        self.applica.setToolTip("Add a step to the current pipeline")

        #Eseguire la pipeline
        self.run = QtWidgets.QPushButton(self.centralwidget)
        self.run.setGeometry(QtCore.QRect(335, 335, 70, 33))
        self.run.setObjectName("run")
        self.run.setFont(self.font)
        self.run.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.run.setStyleSheet("background-color: white; font: 75 13pt \"Yu Gothic\";")
        self.run.clicked.connect(self.executePipeline)
        self.run.setToolTip("Run/Execute the current Pipeline")
        self.run.setText("Run")

        #Eseguire uno step(Dopo aver eseguito la pipeline)
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

        # Aggiunta degli step alla pipeline, i.e., le funzioni implementate
        path = ("Functions")
        self.dir = []
        for i in os.listdir(path):
            if i != "__pycache__" and i != "Plot.py":
                self.dir.append(i.rstrip(".py"))
        for x in self.dir:
            self.operazioni.addItem(x.rstrip(".py"))

        MainWindow.setCentralWidget(self.centralwidget)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("NeuroClean", "NeuroClean"))

    """Funzione che viene eseguita per aggiungere step alla pipeline, invocando la finestra per impostare i dati(della funzione in questione)."""
    def clicker(self):
        x = self.operazioni.currentText()
        diz = {}
        for y in self.dir:
            if y == x:
                q = "Functions." + x
                mymodule = importlib.import_module(q)
                check = self.checkWindow(x)  # Utilizzata per controllare se la funzione ha una finestra già implementata

                f = mymodule.Function()

                if check:  # La funzione ha una sua personale finestra
                    if self.rewrite:
                        for key in self.pipeline.pipeline[self.indexModify][x].keys():
                            f.parameters[key]["value"] = self.pipeline.pipeline[self.indexModify][x][key]["value"]
                    k = True
                    if f.needSignal:
                        if self.signal != []:
                            window = mymodule.Window(f.parameters, self.signal[-1])
                            window.setWindowFlags(window.windowFlags() & ~Qt.WindowContextHelpButtonHint)
                            window.setWindowFlags(window.windowFlags() | Qt.WindowMinimizeButtonHint)
                        else:
                            k = False
                            msg = QMessageBox()
                            msg.setWindowTitle("Operation denied")
                            msg.setText(
                                "The function " + x + " cannot be executed yet because it needs a loaded signal")
                            msg.setIcon(QMessageBox.Information)
                            messageInfo = msg.exec()
                            break
                    else:
                            window = mymodule.Window(f.parameters)
                            window.setWindowFlags(window.windowFlags() & ~Qt.WindowContextHelpButtonHint)
                            window.setWindowFlags(window.windowFlags() | Qt.WindowMinimizeButtonHint)
                    if k and window.exec() and window.result():  # window.result() sostituiscilo con segnale reject
                        f.new(window.result())
                        diz[x] = f.parameters
                        if self.rewrite:
                            self.pipeline.addStep(diz, self.indexModify, self.rewrite)
                            self.rewrite = False
                            self.check = True
                        else:
                            self.pipeline.addStep(diz, 0, self.rewrite)
                            self.check = True
                else:  # Si utilizza la window di default
                    if self.rewrite:
                        for key in self.pipeline.pipeline[self.indexModify][x].keys():
                            f.parameters[key]["value"] = self.pipeline.pipeline[self.indexModify][x][key]["value"]
                    X = FunctionWindow(f.parameters, x)
                    X.setWindowFlags(X.windowFlags() & ~Qt.WindowContextHelpButtonHint)
                    X.setWindowFlags(X.windowFlags() | Qt.WindowMinimizeButtonHint)
                    if X.exec():
                        f.new(X.result())
                        diz[x] = f.parameters
                        if self.rewrite:
                            self.pipeline.addStep(diz, self.indexModify, self.rewrite)
                            self.rewrite = False
                            self.check = True
                        else:
                            self.pipeline.addStep(diz, 0, self.rewrite)
                            self.check = True

    """Caricamento nella Main Window del segnale """
    def SetSignal(self, signal):
        self.segnale = signal

    """Modifica di uno step della pipeline"""
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

    """Salvataggio pipeline"""
    def savePipeline(self):
        if self.pipeline.directory != "":
            name = QFileDialog.getSaveFileName(caption="Choose the directory where save your work",
                                               directory=self.pipeline.directory)
        else:
            name = QFileDialog.getSaveFileName(caption="Choose the directory where save your work")
        self.pipeline.save(name[0])

    """Caricamento di una pipeline già esistente"""
    def loadPipeline(self):
        name = QFileDialog.getOpenFileName(
            caption='Select pipeline',
            directory=os.getcwd(),
            filter='JSON File (*.json);',
        )
        if name[0] != '':
            self.pipeline.load(name[0])

    """Esecuzione della pipeline step by step + controllo che il primo step sia quello di apertura di un segnale"""
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
                    if i == 0:
                        self.signal.append(mymodule.Function().run(self.pipeline.pipeline[i][key]["file"]))
                    else:
                        if hasattr(mymodule.Function(), "directory"):
                            self.signal.append(mymodule.Function().run(self.pipeline.pipeline[i][key], self.signal[- 1],
                                                                       self.pipeline.directory))
                        else:
                            self.signal.append(
                                mymodule.Function().run(self.pipeline.pipeline[i][key], self.signal[- 1]))
                else:
                    try:
                       mymodule = importlib.import_module("Functions.Plot")
                       plot = self.pipeline.pipeline[i]
                       f = mymodule.Function(self.signal[-1], plot["plot"], self.pipeline.directory)
                       f.run()
                    except RuntimeError as e:
                        msg = QMessageBox()
                        msg.setWindowTitle("Operation denied")
                        msg.setText(str(e))
                        msg.setIcon(QMessageBox.Warning)
                        messageError = msg.exec()
        if self.signal:
            """Salvataggio del segnale"""
            self.pipeline.addSignal(self.signal)
            self.pipeline.saveSignal()
            self.exec.setVisible(True)

    """Esecuzione di un singolo step"""
    def execStep(self):
        if self.signal:
            x = self.operazioni.currentText()
            for y in self.dir:
                if y == x:
                    q = "Functions." + x
                    mymodule = importlib.import_module(q)
                    f = mymodule.Function()
                    check = self.checkWindow(x)  # Controlla la presenza o meno della finestra di default per la funzione in esecuzione
                    diz = {}
                    if check:  # La funzione ha una sua personale finestra
                        k = True
                        if f.needSignal:
                            if self.signal:
                                window = mymodule.Window(f.parameters, self.signal[-1])
                                window.setWindowFlags(window.windowFlags() & ~Qt.WindowContextHelpButtonHint)
                                window.setWindowFlags(window.windowFlags() | Qt.WindowMinimizeButtonHint)
                            else:
                                k = False
                        else:
                            window = mymodule.Window(f.parameters)
                            window.setWindowFlags(window.windowFlags() & ~Qt.WindowContextHelpButtonHint)
                            window.setWindowFlags(window.windowFlags() | Qt.WindowMinimizeButtonHint)
                        if k and window.exec() and window.result():  # window.result() sostituiscilo con segnale reject
                            f.new(window.result())
                            diz[x] = f.parameters
                            self.pipeline.addStep(diz, 0, self.rewrite)
                            self.check = True
                    else:  # Si utilizza la window di default
                        X = FunctionWindow(f.parameters, x)
                        if X.exec():
                            f.new(X.result())
                            diz[x] = f.parameters
                            self.pipeline.addStep(diz, 0, self.rewrite)
                            self.check = True
                    try:
                        if diz.keys():
                            key = list(diz.keys())[0]
                            if key == "OpenFile":
                                self.signal.append(mymodule.Function().run(self.pipeline.pipeline[-1][key]["file"]))
                            else:
                                if hasattr(mymodule.Function(), "directory"):
                                    self.signal.append(
                                        mymodule.Function().run(self.pipeline.pipeline[-1][key], self.signal[- 1],
                                                                self.pipeline.directory))
                                else:
                                    self.signal.append(
                                        mymodule.Function().run(self.pipeline.pipeline[-1][key], self.signal[- 1]))
                        else:
                            pass
                    except RuntimeError as e:
                        msg = QMessageBox()
                        msg.setWindowTitle("Operation denied")
                        msg.setText(str(e))
                        msg.setIcon(QMessageBox.Warning)
                        messageError = msg.exec()
                        self.pipeline.removeStep(diz, 0, False)

    """Esegue il plot scelto"""
    def execPlot(self):
        if self.signal:
            try:
                mymodule = importlib.import_module("Functions.Plot")
                plot = self.pipeline.pipeline[-1]
                f = mymodule.Function(self.signal[-1], plot["plot"], self.pipeline.directory)
                f.run()
            except RuntimeError as e:
                msg = QMessageBox()
                msg.setWindowTitle("Operation denied")
                msg.setText(str(e))
                msg.setIcon(QMessageBox.Warning)
                messageError = msg.exec()
        else:
            pass

    """Controlla se la funzione abbia o meno una finestra sua"""
    def checkWindow(self, function: str):
        test = os.path.join("Functions", function + ".py")
        with open(test) as temp_f:
            datafile = temp_f.readlines()
        for line in datafile:
            if 'class Window(QDialog):' in line:
                return True
        return False

    """Restituisce informazioni sul segnale"""
    def infoSignal(self):
        if self.signal:
            self.x = InfoWindow(self.signal[-1].info)
            self.x.show()
            self.label.setText("Complete information about the signal are printed in the terminal")
            print(self.signal[-1].get_montage())
