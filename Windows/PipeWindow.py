from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QListWidget, QGridLayout, QMainWindow, QWidget, QDialogButtonBox, \
    QPushButton, QHBoxLayout, QLineEdit, QLabel, QSpinBox, QComboBox, QTreeWidget, QTreeWidgetItem

from Pipeline import *


class PipelineWindow(QDialog):

    def __init__(self, Pipeline: Pipeline):
        super().__init__()
        self.index = None
        self.setObjectName("Pipeline")
        self.setWindowTitle("Pipeline")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint & ~Qt.WindowMaximizeButtonHint)
        self.setWindowFlags(self.windowFlags() | Qt.WindowMinimizeButtonHint)
        self.pipeline = Pipeline
        self.pipe = Pipeline.return_pipeline()

        layout = QGridLayout()
        self.setLayout(layout)
        self.listwidget = QTreeWidget()

        self.listwidget.setColumnCount(2)
        self.listwidget.setHeaderLabels(['CheckBox', 'Pipeline'])
        for j in range(0, len(self.pipe)):
            item = QTreeWidgetItem(self.listwidget)
            item.setCheckState(0, QtCore.Qt.Unchecked)
            y = self.pipe[j]
            item.setText(1, str(y))
            self.listwidget.addTopLevelItem(item)

        # Bottoni + stile pagina?
        layout.addWidget(self.listwidget)

        self.buttonSwap = QPushButton()
        self.buttonSwap.setToolTip("Click to swap the position of two steps")
        self.buttonSwap.setText("Swap")
        self.buttonSwap.setStyleSheet("background-color: #4CAF50; border: none; color: white; padding: 6px 12px; \n"
                                      "text-align: center; text-decoration: none; display: inline-block; font-size: 12px;")
        self.buttonModify = QPushButton()
        self.buttonModify.setToolTip("Select a step to edit its parameters")
        self.buttonModify.setText("Modify")
        self.buttonModify.setStyleSheet(
            "background-color: #008CBA; border: none; color: white; padding: 6px 12px; \n"
            "text-align: center; text-decoration: none; display: inline-block; font-size: 12px;")
        self.buttonDelete = QPushButton()
        self.buttonDelete.setToolTip("Click to remove one or more steps from the pipeline")
        self.buttonDelete.setText("Delete")
        self.buttonDelete.setStyleSheet(
            "background-color: #f44336; border: none; color: white; padding: 6px 12px; \n"
            "text-align: center; text-decoration: none; display: inline-block; font-size: 12px;")

        layout.addWidget(self.buttonSwap)
        layout.addWidget(self.buttonModify)
        layout.addWidget(self.buttonDelete)
        self.buttonbox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addWidget(self.buttonbox)
        self.buttonbox.accepted.connect(self.accept)
        self.buttonModify.clicked.connect(self.modify)
        self.buttonDelete.clicked.connect(self.delete)
        self.buttonSwap.clicked.connect(self.swap)
        self.buttonbox.rejected.connect(self.reject)
        self.buttonModify.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.buttonSwap.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.buttonDelete.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.buttonbox.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        layout.setSizeConstraint(QVBoxLayout.SetFixedSize)

    def modify(self):
        j = 0
        for i in range(0, self.listwidget.topLevelItemCount()):
            if self.listwidget.topLevelItem(i).checkState(0) == QtCore.Qt.Checked:
                self.index = i
                j = j + 1
        if j != 1 or list(self.pipeline.pipeline[self.index].keys())[0] == "plot":
            return
        else:
            self.accept()

    def swap(self):
        x = []
        j = 0
        for i in range(0, self.listwidget.topLevelItemCount()):
            if self.listwidget.topLevelItem(i).checkState(0) == QtCore.Qt.Checked:
                x.append(self.pipeline.pipeline[i])
                j = j + 1
        if j != 2:
            return
        k, l = self.pipeline.swap(x)
        self.listwidget.topLevelItem(k).setText(1, str(x[1]))
        self.listwidget.topLevelItem(l).setText(1, str(x[0]))
        self.pipe = self.pipeline.return_pipeline()

    def delete(self):
        listItems = []
        for i in range(0, self.listwidget.topLevelItemCount()):
            if self.listwidget.topLevelItem(i).checkState(0) == QtCore.Qt.Checked:
                listItems.append([self.listwidget.topLevelItem(i), self.pipeline.pipeline[i]])
            # listItems.append(self.pipeline.pipeline[i])
        if not listItems: return
        for item in listItems:
            itemIndex = self.listwidget.indexOfTopLevelItem(item[0])
            self.listwidget.takeTopLevelItem(itemIndex)
            y = self.pipe.index(item[1])
            self.pipe.remove(item[1])
            self.pipeline.updatePipeline(self.pipe)
