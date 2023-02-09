from matplotlib.figure import Figure
import matplotlib as mpl

class Function:
    """Funzione che controlla i plot del segnale + setta la directory di default per salvare i plot"""
    def __init__(self, signal, type, directory):
        self.signal = signal
        self.parameters = {"plot" : type}
        mpl.rcParams["savefig.directory"] = directory

    def run(self):
        if(self.parameters["plot"] == "plot()"):
            y = self.signal.copy()
            fig: Figure = y.plot(use_opengl=True)
            win = fig.canvas.manager.window
            win.setWindowTitle("Plot of raw data")
            fig.show()
        elif (self.parameters["plot"] == "compute_psd().plot()"):
            fig: Figure = self.signal.compute_psd().plot()
            win = fig.canvas.manager.window
            win.setWindowTitle("Power spectral density")
            fig.show()
        elif (self.parameters["plot"] == "plot_locations()"):
            fig: Figure = self.signal.plot_sensors(show_names=True)
            win = fig.canvas.manager.window
            win.setWindowTitle("Plot of sensors positions/ Montage")
            fig.show()
