from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt,  QSortFilterProxyModel
from PyQt5.QtWidgets import (
  QDialog,
  QStyledItemDelegate,
  QComboBox,
  QDialogButtonBox,
  QVBoxLayout,
  QAbstractItemView,
  QTableView
)
from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtCore import Slot
from mne.io.pick import get_channel_type_constants, channel_type


channel_types = [k.upper() for k in get_channel_type_constants().keys()]

class ChannelProperties(QDialog):

    def __init__(self,  info):
        super().__init__()
        self.setObjectName("Channel Properties")
        self.setWindowTitle("Channel Properties")
        self.resize(431, 431)

        self.model = QStandardItemModel(info["nchan"], 4)
        self.model.setHorizontalHeaderLabels(["#", "Label", "Type", "Bad"])
        for index, ch in enumerate(info["chs"]):
            item = QStandardItem()
            item.setData(index, Qt.DisplayRole)
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            self.model.setItem(index, 0, item)
            self.model.setItem(index, 1, QStandardItem(ch["ch_name"]))
            kind = channel_type(info, index).upper()
            self.model.setItem(index, 2, QStandardItem(str(kind)))
            self.bad = QStandardItem()
            self.bad.setData(ch["ch_name"] in info["bads"], Qt.UserRole)
            self.bad.setCheckable(True)
            self.bad.setEditable(False)
            checked = ch["ch_name"] in info["bads"]
            self.bad.setCheckState(Qt.Checked if checked else Qt.Unchecked)
            self.model.setItem(index, 3, self.bad)

        self.model.itemChanged.connect(bad_changed)
        self.proxymodel = MySortFilterProxyModel()
        self.proxymodel.setDynamicSortFilter(False)
        self.proxymodel.setSourceModel(self.model)

        self.view = QTableView()
        self.view.setModel(self.proxymodel)
        self.view.setItemDelegateForColumn(2, ComboBoxDelegate(self.view))
        self.view.setEditTriggers(QAbstractItemView.AllEditTriggers)
        self.view.verticalHeader().setVisible(False)
        self.view.horizontalHeader().setStretchLastSection(True)
        self.view.setShowGrid(False)
        self.view.setSelectionMode(QAbstractItemView.NoSelection)
        self.view.setSortingEnabled(True)
        self.view.sortByColumn(0, Qt.AscendingOrder)

        vbox = QVBoxLayout(self)
        vbox.addWidget(self.view)
        self.buttonbox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        vbox.addWidget(self.buttonbox)
        self.buttonbox.accepted.connect(self.result)
        self.buttonbox.rejected.connect(self.reject)

        self.resize(475, 650)
        self.view.setColumnWidth(0, 70)
        self.view.setColumnWidth(1, 155)
        self.view.setColumnWidth(2, 90)


class MySortFilterProxyModel(QSortFilterProxyModel):
    """Add ability to filter on Qt.UserRole if Qt.DisplayRole is None.
    This is useful for the 'Bad' column, which stores its data (True/False) as Qt.UserRole
    instead of the default Qt.DisplayRole.
    """
    def lessThan(self, left, right):
        left_data = self.sourceModel().data(left)
        right_data = self.sourceModel().data(right)
        if left_data is None:
            left_data = self.sourceModel().data(left, Qt.UserRole)
        if right_data is None:
            right_data = self.sourceModel().data(right, Qt.UserRole)

        return left_data < right_data

class ComboBoxDelegate(QStyledItemDelegate):
    @Slot()
    def commit_data(self):
        self.commitData().emit(self.sender())
        self.closeEditor().emit(self.sender())

    def createEditor(self, parent, option, index):
        editor = QComboBox(parent)
        editor.addItems(channel_types)
        editor.currentIndexChanged.connect(self.commit_data)
        return editor

    def setEditorData(self, editor : QtWidgets.QComboBox, index):
        value = index.model().data(index, Qt.EditRole)
        editor.setCurrentIndex(editor.findText(value))
        editor.showPopup()

    def setModelData(self, editor: QtWidgets.QComboBox, model, index):
        value = editor.currentText()
        model.setData(index, value, Qt.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)

@Slot()
def bad_changed(item):
    if item.checkState() == Qt.Checked:
        item.setData(True, Qt.UserRole)
    else:
        item.setData(False, Qt.UserRole)