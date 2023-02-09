import mne.io.base
from PyQt5.QtWidgets import QDialog, QWidget, QLabel, QGridLayout, QListWidget


class InfoWindow(QWidget):

    def __init__(self, InfoObj: mne.io.base.BaseRaw):
        super().__init__()
        self.setObjectName("InfoSignal")
        self.setWindowTitle("Information about the signal")
        self.window_width, self.window_height = 400, 475
        self.setMinimumSize(self.window_width, self.window_height)
        self.setStyleSheet("background-color:#8C8C8C")
        self.info = InfoObj

        layout = QGridLayout()
        self.setLayout(layout)
        self.listwidget = QListWidget()
        self.listwidget.setStyleSheet("background: transparent;\n"
                                      "font: 75 11pt \"Yu Gothic\";\n"
                                      "color: rgb(255, 255, 255);\n"
                                      "text-align: center;\n"
                                      "")

        self.listwidget.insertItem(0, str(self.info))
        self.listwidget.insertItem(1,
                                   "----------------------------------------------------------------------------------detailed view---------------------------------------------------------------------------------------------------------------")
        keys = ['file_id', 'subject_info', 'device_info', 'meas_id', 'proj_id', 'experimenter',
                'description', 'bads', 'ch_names', 'events']
        i = 2
        for key in keys:
            if key == 'ch_names' or key == 'bads':
                if len(self.info.__getitem__(key)) > 9:
                    x = "[ "
                    j = 0
                    for i in range(0, len(self.info.__getitem__(key))):
                        x += self.info.__getitem__(key)[i] + " ,  "
                        j += 1
                        if (j == 13):
                            x += '\n'
                            j = 0
                    x = x.rstrip()
                    x = x.rstrip(",")
                    x += " ]"
                else:
                    x = str(self.info.__getitem__(key))
                self.listwidget.insertItem(i, str(key) + " : \n " + x + "\n")
                i += 1
            else:
                self.listwidget.insertItem(i, str(key) + " -> " + str(self.info.__getitem__(key)) + "\n")
                i += 1
        layout.addWidget(self.listwidget)
