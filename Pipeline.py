"""Classe Pipeline, si occupa di gestire e mantenere la pipeline utilizzata nel preprocessing, inoltre:
   1) Salva la pipeline utilizzata
   2) Esegue una pipeline
"""
import os


class Pipeline:
    """Funzione per gestire le pipeline:\n
      -Esecuzione;/n
      -Modifica;\n
      -Salvataggio;/n
      Inoltre salva il segnale e il codice Python(deprecabile)
    """

    """Definizione parametri"""
    def __init__(self):
        self.pipeline = []
        self.signal = None
        self.operations = []
        self.programma = ""
        self.imports = ["import mne", "import os"]  # VEDITI COME CANCELLARE ELEMENTI RIPETUTI IN UNA LISTA!!!!!
        self.rewrite = False
        self.directory = ""

    """Definizione directory di lavoro"""
    def Directory(self, nomefile):
        from datetime import datetime
        tmp = nomefile.split("/")
        self.pipesave = tmp[len(tmp) - 1]
        if self.directory == "":
            tmp[len(tmp) - 1] = "PipelineWork_" + str(datetime.today().strftime('%Y%m%d_%H%M'))
            for x in tmp:
                self.directory += x + "/"

    """Salvataggio pipeline"""
    def save(self, nomefile: str):
        import json
        if self.directory == "":
            self.Directory(nomefile)
            os.mkdir(self.directory)
        else:
            self.Directory(nomefile)
        print(self.directory)
        nomeprogramma = self.directory + "codice.py"
        nomefile = self.directory + self.pipesave

        # CODICE
        file = open(nomeprogramma, "w")
        file.write(self.exe())
        file.close()

        # PIPELINE
        data = {"pipeline": self.pipeline, "imports": self.imports}
        with open(nomefile + ".json", "w") as outfile:
            json.dump(data, outfile, indent=1)
        self.saveSignal()

    """Salvataggio segnale --> quale formato?"""
    def saveSignal(self):
        # SEGNALE
        if self.signal is not None:  # Funzione esterna va fatta
            from datetime import datetime
            nomesig = self.directory + "signal" + str(datetime.today().strftime('%H%M')) + ".fif"
            self.signal[-1].save(nomesig, overwrite=True)
        else:
            pass

    """La funzione load legge automaticamente il contenuto del file, rappresentandolo come dizionario. """
    def load(self, path: str):
        import json
        data = json.load(open(path))["pipeline"]
        for y in data:
            self.pipeline.append(y)
        libraries = json.load(open(path))["imports"]
        for k in libraries:
            if k not in self.imports:  # Per evitare doppioni, ma serve?
                self.imports.append(k)

    """Esecuzione pipeline"""
    def exe(self):
        for k in self.imports:
            self.programma += k + "\n"
        self.programma += "\n"
        for x in self.pipeline:
            for key in x.keys():
                if key != "plot":
                    values = ""
                    for keyParam in x[key].keys():
                        if values != "":
                            values += " , "
                        if x[key][keyParam]["value"] != "":
                            if x[key][keyParam]["type"] == "str":
                                values += f'"{x[key][keyParam]["value"]}"'
                            else:
                                values += str(x[key][keyParam]["value"])
                        else:
                            values += "None"
                    self.programma += ("signal  =  Functions." + str(key) + ".run(" + values + ")\n")
                else:
                    self.programma += ("signal." + str(x["plot"]) + "\n")
        return self.programma

    def plot_data(self):
        self.pipeline.append({"plot": "plot()"})
        # self.operations.append({"plot_data": None})

    def plot_psd(self):
        self.pipeline.append({"plot": "compute_psd().plot()"})
        # self.operations.append({"plot_psd": None})

    def plot_locations(self):
        self.pipeline.append({"plot": "plot_locations()"})
        # self.operations.append({"plot_Locations": None})

    def return_pipeline(self) -> list:
        return self.pipeline

    """Aggiunge uno step + i suoi parametri alla pipeline"""
    def addStep(self, x: dict, index: int, rewrite):
        if rewrite:
            self.pipeline[index] = x
        else:
            self.pipeline.append(x)

    """Rimuove uno step + i suoi parametri alla pipeline"""
    def removeStep(self, x: dict, index: int, rewrite):
        if rewrite:
            self.pipeline.pop(index)
        else:
            self.pipeline.remove(x)

    def updatePipeline(self, Pipeline):
        self.pipeline = Pipeline

    """Definisce il segnale in tutti gli step temporali"""
    def addSignal(self, signalStates: list):
        self.signal = signalStates

    """Scambia due step, dal punto di vista dell'ordine cronologico con il quale sono eseguiti"""
    def swap(self, x: list):
        tmp1 = x[0]
        y = self.pipeline.index(x[0])  # Old x1
        z = self.pipeline.index(x[1])  # Old x2
        self.pipeline[y] = self.pipeline[z]
        self.pipeline[z] = tmp1
        return y, z
