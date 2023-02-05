import mne
import numpy as np
from matplotlib.pyplot import *
import matplotlib.pyplot as plt
from Pipeline import Pipeline

"""Classe Segnale, si occupa di gestire e mantenere il segnale che viene preso grezzo in input e 
   salvato 'pulito' in output
"""
class Segnale:
    # Costruttore del segnale
    def __init__(self, fname):
        raw = mne.io.read_raw(fname, preload=True)
        raw.crop(0, 60).load_data()  # Uso una frazione per test
        self.signal = raw
        #self.default_filtering() # Nei dataset di esempio non funziona, i.e., l'alimentazione USA va a 60hz

    # Data una stringa/path in ingresso cerca un segnale da caricare, se inadatto l'eccezione verrà presa dal metodo che lo invoca
    def insert_data(self, fname):
        raw = mne.io.read_raw(fname, preload=True)
        raw.load_data()
        self.signal = raw

    def plot_data(self):
        y = self.signal.copy()
        fig: Figure = y.plot(use_opengl=True)
        win = fig.canvas.manager.window
        win.setWindowTitle("Plot of raw data")
        fig.show()

    def plot_psd(self):
        fig: Figure = self.signal.compute_psd().plot()
        win = fig.canvas.manager.window
        win.setWindowTitle("Power spectral density")
        fig.show()

    def plot_locations(self):
        fig: Figure = self.signal.plot_sensors(show_names=True)
        win = fig.canvas.manager.window
        win.setWindowTitle("Plot of sensors positions/ Montage")
        fig.show()

    def return_info(self) -> object:
        return self.signal.info

    def default_filtering(self):
        picks = mne.pick_types(self.signal.info,
                               stim=False, exclude='bads')
        freqs = (50, 100, 150, 200)
        self.signal.notch_filter(np.arange(start=50, stop=251, step=50))
        return None

    def filtering(self, low, high):
        if((high != None) and (low == None)):
            self.signal.filter(l_freq=high, h_freq=None)
            return 2
        elif((low != None) and (high == None)):
            self.signal.filter(h_freq=low, l_freq=None)
            return 3
        elif ((high > low)):
            self.signal.filter(l_freq=low, h_freq=high)
            return 1
        return 0

    """, names=None, types=None"""
    def set_channel_properties(self, bads=None):
        if bads != self.signal.info["bads"]:
            self.signal.info["bads"] = bads
            #self.pipeline.append(f"data.info['bads'] = {bads}")
        """
                if names:
            mne.rename_channels(self.current["data"].info, names)
            self.history.append(f"mne.rename_channels(data.info, {names})")
        if types:
            self.current["data"].set_channel_types(types)
            self.history.append(f"data.set_channel_types({types})")
        """