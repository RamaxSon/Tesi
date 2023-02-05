"""Classe Pipeline, si occupa di gestire e mantenere la pipeline utilizzata nel preprocessing, inoltre:
   1) Salva la pipeline utilizzata
   2) Esegue una pipeline
"""
import os

class Pipeline:
    def __init__(self):
        self.pipeline = []
        self.signal = None
        self.operations = []
        self.programma = ""
        self.imports = ["import mne", "import os"]  # VEDITI COME CANCELLARE ELEMENTI RIPETUTI IN UNA LISTA!!!!!
        self.rewrite = False


    def Directory(self, nomefile):
        from datetime import datetime
        self.directory = ""
        tmp = nomefile.split("/")
        self.pipesave = tmp[len(tmp) - 1]
        tmp[len(tmp) - 1] = "PipelineWork_" + str(datetime.today().strftime('%Y%m%d_%H%M'))
        for x in tmp:
            self.directory += x + "/"


    # Far salvare nome file come "/tmp/nomefile" SIUUUUM
    def save(self, nomefile: str):
        import json
        self.Directory(nomefile)
        os.mkdir(self.directory)
        nomefile = self.directory + self.pipesave
        nomeprogramma = self.directory + "codice.py"

        # CODICE
        file = open(nomeprogramma, "w")
        file.write(self.exe())
        file.close()

        # PIPELINE
        data = {"pipeline": self.pipeline, "imports": self.imports}
        with open(nomefile + ".json", "w") as outfile:
            json.dump(data, outfile, indent=1)
        self.saveSignal()

    def saveSignal(self):
        # SEGNALE
        if self.signal is not None:  # Funzione esterna va fatta
            from datetime import datetime
            nomesig = self.directory + "signal" + str(datetime.today().strftime('%H%M'))+".fif"
            self.signal[-1].save(nomesig)
        else:
            pass

    # PER LA LOAD IMPONI .json COME FORMATO
    """La funzione load legge automaticamente il contenuto del file, rappresentandolo come dizionario. """
    def load(self, path: str):
        import json
        data = json.load(open(path))["pipeline"]
        for y in data:
            self.pipeline.append(y)
        libraries = json.load(open(path))["imports"]
        for k in libraries:
            if k not in self.imports:  #Per evitare doppioni, ma serve?
                self.imports.append(k)

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

    def x(self, x: dict, index: int, rewrite):  # operations : dict
        if rewrite:
            self.pipeline[index] = x
        else:
            self.pipeline.append(x)

    def updatePipeline(self, Pipeline):
        self.pipeline = Pipeline

    def addSignal(self, signalStates : list):
        self.signal = signalStates

    def swap(self, x: list):
        tmp1 = x[0]
        y = self.pipeline.index(x[0])  # Old x1
        z = self.pipeline.index(x[1])  # Old x2
        self.pipeline[y] = self.pipeline[z]
        self.pipeline[z] = tmp1
        return y, z
