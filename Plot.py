import sys
import time

import numpy as np

from matplotlib.backends.qt_compat import QtWidgets
from matplotlib.backends.backend_qtagg import (
    FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure


class PlotWindow(QtWidgets.QMainWindow):
    def __init__(self, f: Figure):
        super().__init__()
        self._main = QtWidgets.QWidget()
        self.setCentralWidget(self._main)
        layout = QtWidgets.QVBoxLayout(self._main)
        self.figure = f
        self.canvas = FigureCanvasQTAgg(self.figure)

        layout.addWidget(self.canvas)
        layout.addWidget(NavigationToolbar(self.canvas, self))

        self._dynamic_ax = self.canvas.figure.subplots()
       # self._line, = self._dynamic_ax.plot()
       # self._timer = self.canvas.new_timer(50)
       #self._timer.add_callback(self._update_canvas)
        #self._timer.start()

    def _update_canvas(self):
        t = np.linspace(0, 10, 101)
        self._line.set_data(t, np.sin(t + time.time()))
        self._line.figure.canvas.draw()