import mne
from PyQt5.QtWidgets import QMessageBox

class Function:
    """
    Funzione che si occupa di eseguire il filtering/filtraggio in frequenza del segnale, potendo scegliere tra: \n
    -Filtro passa basso (Ftl); \n
    -Filtro passa alto (Fth); \n
    -Filtro passa banda (Ftl < Fth) \n
    -Filtro notch.
    """

    """Definizione parametri della funzione"""
    def __init__(self):
        self.needSignal = False
        self.parameters = {"lowpass": {"type": "int", "value": None, "default": "0"},
            "highpass": {"type": "int", "value": None, "default": "0"},
                "notch": {"type": "int", "value": None, "default": "0"}}

    """Imposta i parametri della funzione"""
    def new(self, args):
        for key in args.keys():
            self.parameters[key]["value"] = args[key]["value"]

    """Esecuzione della funzione: \n
       1)Controllo se vengono rispettati vincoli logici tra le frequenze di taglio; \n
       2)Esecuzione del filtraggio scelto; \n
       3)Ritorno del risultato (segnale) \n
    """
    def run(self, args, signal : mne.io.read_raw):
        self.new(args)
        try:
            if self.parameters["lowpass"]["value"] != 0 and self.parameters["highpass"]["value"] == 0:  # passaBasso
                return signal.filter(h_freq=self.parameters["lowpass"]["value"], l_freq=None)

            elif self.parameters["highpass"]["value"] != 0 and self.parameters["lowpass"]["value"] == 0:  # passaAlto
                return signal.filter(l_freq=self.parameters["highpass"]["value"], h_freq=None)

            elif self.parameters["highpass"]["value"] != 0 and self.parameters["lowpass"]["value"] != 0 and (
                    self.parameters["lowpass"]["value"] <= self.parameters["highpass"]["value"]):  # passaBanda
                return signal.filter(l_freq=self.parameters["lowpass"]["value"],
                                     h_freq=self.parameters["highpass"]["value"])
            elif self.parameters["highpass"]["value"] == 0 and self.parameters["lowpass"]["value"] == 0 and (
                    self.parameters["notch"]["value"] != 0):
                import numpy as np

                if 3*self.parameters["notch"]["value"] <= signal.info["sfreq"]/2:
                     return signal.notch_filter(np.arange(self.parameters["notch"]["value"], 3*self.parameters["notch"]["value"], self.parameters["notch"]["value"]))
                elif 2*self.parameters["notch"]["value"] <= signal.info["sfreq"]/2:
                     return signal.notch_filter(np.arange(self.parameters["notch"]["value"], 2*self.parameters["notch"]["value"], self.parameters["notch"]["value"]))
                else:
                    return signal.notch_filter(self.parameters["notch"]["value"])
            else:
                return signal
        except ValueError as e:
           msg = QMessageBox()
           msg.setWindowTitle("Operation denied")
           msg.setText(str(e))
           msg.setIcon(QMessageBox.Warning)
           messageError = msg.exec()
           return signal
        except TypeError as e:
           msg = QMessageBox()
           msg.setWindowTitle("Operation denied")
           msg.setText(str(e))
           msg.setIcon(QMessageBox.Warning)
           messageError = msg.exec()
           return signal

