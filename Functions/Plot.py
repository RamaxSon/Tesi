from PyQt5.QtWidgets import QDialog, QVBoxLayout, QDialogButtonBox, QPushButton, QLabel, QGridLayout, \
    QFileDialog, QMessageBox
from matplotlib import pyplot as plt
from matplotlib.figure import Figure
import matplotlib as mpl

class Function:
    """Funzione che controlla i plot del segnale + setta la directory di default per salvare i plot"""
    def __init__(self, signal, type, directory):
        self.signal = signal
        self.parameters = {"plot" : type}
        mpl.rcParams["savefig.directory"] = directory

    def run(self):
        try:
            if self.parameters["plot"] == "plot()":
                y = self.signal.copy()
                fig: Figure = y.plot(use_opengl=True)
                win = fig.canvas.manager.window
                win.setWindowTitle("Plot of raw data")
                fig.show()
            elif self.parameters["plot"] == "compute_psd().plot()":
                fig: Figure = self.signal.compute_psd().plot()
                win = fig.canvas.manager.window
                win.setWindowTitle("Power spectral density")
                fig.show()
            elif self.parameters["plot"] == "plot_locations()":
                fig: Figure = self.signal.plot_sensors(show_names=True, sphere='auto')  # , sphere='auto'
                win = fig.canvas.manager.window
                win.setWindowTitle("Plot of sensors positions/ Montage")
                fig.show()
            elif self.parameters["plot"] == "plot_events()":
                """
                events, event_id = events_from_annotations(self.signal)
                annotations = Annotations.from_events(events, self.signal.info['sfreq'], event_id)
                self.signal.set_annotations(annotations)
                fig: Figure = viz.plot_events(events, sfreq=self.signal.info['sfreq'])
                win = fig.canvas.manager.window
                win.setWindowTitle("Plot of events")
                fig.show()
                """
                pass
        except ValueError as e:
            msg = QMessageBox()
            msg.setWindowTitle("Operation denied")
            msg.setText(str(e))
            msg.setIcon(QMessageBox.Warning)
            messageError = msg.exec()

class WindowEvents(QDialog):
    def __init__(self):
        super().__init__()
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
        self.template.clicked.connect(self.InputEvents)
        grid.addWidget(self.template, left, right)
        right -= 1
        left += 1

        vbox.addLayout(grid)
        self.buttonbox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        vbox.addWidget(self.buttonbox)
        self.buttonbox.accepted.connect(self.result)
        self.buttonbox.rejected.connect(self.reject)
        vbox.addWidget(self.buttonbox)
        vbox.setSizeConstraint(QVBoxLayout.SetFixedSize)

    def InputEvents(self):
        import os
        response = QFileDialog.getOpenFileName(
            parent=self,
            caption='Select a template for montage',
            directory=os.getcwd(),
        )
        if response[0] != '':
            self.template.setText(response[0])

    def result(self):
        return self.template if self.template else None