import mne
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QGridLayout, QLabel, QLineEdit, QDialogButtonBox, QWidget

class Function:

    def __init__(self):
        self.self = True
        self.parameters = {"lowpass": {"type": "int", "value": None, "default": "0"},
            "highpass": {"type": "int", "value": None, "default": "0"}}

    def new(self, args): #filter, high, low
        for key in args.keys():
            self.parameters[key]["value"] = args[key]["value"]

    def run(self, args, signal : mne.io.read_raw):
        self.new(args)
        if self.parameters["lowpass"]["value"] != 0 and self.parameters["highpass"]["value"] == 0: #passaBasso
            return signal.filter(h_freq=self.parameters["lowpass"]["value"], l_freq=None)

        elif self.parameters["highpass"]["value"] != 0 and self.parameters["lowpass"]["value"] == 0:  # passaAlto
            return signal.filter(l_freq=self.parameters["highpass"]["value"], h_freq=None)

        elif self.parameters["highpass"]["value"] != 0 and self.parameters["lowpass"]["value"] != 0 and (self.parameters["lowpass"]["value"] <= self.parameters["highpass"]["value"]):  # passaBanda
            return signal.filter(l_freq=self.parameters["lowpass"]["value"], h_freq=self.parameters["highpass"]["value"])
        else:
            return signal #No Change?

