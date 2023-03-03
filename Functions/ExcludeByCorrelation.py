import mne
from PyQt5.QtWidgets import QMessageBox


class Function:
    """
    Funzione che va ad impostare come bad i canali con una bassa correlazione rispetto ai loro vicini.
    """

    """Definizione parametri della funzione"""
    def __init__(self):
        self.needSignal = False
        self.parameters = {"soglia": {"type": "float", "value": None, "default": "0.5"},
                           "distance": {"type": "float", "value": None, "default": "0.3",
                                        "desc": "Esprimere la distanza in metri nella quale calcolare la correlazione con i vicini(Considerare che verranno calcolato come cm)"}}

    """Imposta i parametri della funzione"""
    def new(self, args):
        for key in args.keys():
            self.parameters[key]["value"] = args[key]["value"]

    """Calcolo distanza euclidea tra due punti nello spazio {x,y,z}"""
    def euclideanDistance(self, vett1, vett2):
        from math import sqrt
        d = sqrt((float(vett2[0]) - float(vett1[0]))**2 + (float(vett2[1]) - float(vett1[1]))**2 + (float(vett2[1]) - float(vett1[2]))**2)
        return d

    """Calcolo della correlazione tra gli elettrodi rispetto ai loro vicini"""
    def Correlation(self):
        from scipy.stats import pearsonr
        from statistics import mean
        correlations = {}
        means = {}
        excluded = []
        for i in range(0, len(self.signal.info["ch_names"])):
            correlations[self.signal.info["ch_names"][i]] = []
            for j in range(0, len(self.signal.info["ch_names"])):
                if i != j and self.euclideanDistance(self.signal.info["chs"][i]["loc"][:3], self.signal.info["chs"][j]["loc"][:3]) <= float(self.parameters["distance"]["value"]):
                    corr_coef = pearsonr(self.signal.get_data(self.signal.info["ch_names"][i])[0], self.signal.get_data(self.signal.info["ch_names"][j])[0])
                    correlations[self.signal.info["ch_names"][i]].append(corr_coef[0])
            try:
                means[self.signal.info["ch_names"][i]] = mean(correlations[self.signal.info["ch_names"][i]])
            except ValueError as e:
                print("Error in the channel : "+self.signal.info["ch_names"][i])
                print(e)
                print("Maybe the distance is too small, check it and remember it is in centimeters")
                print("---------------------")
        for index in means.keys():
            if means[index] <= float(self.parameters["soglia"]["value"]):
                excluded.append(index)
        self.parameters["excluded"] = {}
        self.parameters["excluded"]["value"] = excluded

    """Canali con poca correlazione impostati come bad"""
    def run(self, args, signal: mne.io.read_raw):
        self.new(args)
        self.signal = signal
        try:
            self.Correlation()
            if self.parameters["excluded"]["value"]:
                self.signal.info["bads"] = self.parameters["excluded"]["value"]
                #self.signal.drop_channels(self.parameters["excluded"]["value"])
            return self.signal
        except ValueError as e:
            msg = QMessageBox()
            msg.setWindowTitle("Operation denied")
            msg.setText(str(e))
            msg.setIcon(QMessageBox.Warning)
            messageError = msg.exec()
            return self.signal
