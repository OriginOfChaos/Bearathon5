from copy import deepcopy
from json import dump as json_dump, load as json_load
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import (QMainWindow, QGroupBox, QFileDialog, QMenuBar, QMenu, QFormLayout,
                                QPushButton, QSizePolicy, QGridLayout, QDialog, QDialogButtonBox,
                                QSpinBox, QCheckBox, QLabel, QMessageBox, QToolBar, QLineEdit,
                                QHBoxLayout, QWidget, QScrollArea, QVBoxLayout, QTabWidget, QComboBox)
from os import path as os_path

from bingo import Bingo

class App(QMainWindow):
    def __init__(self):
        super().__init__()

        self.bingo = Bingo("", 0, False, False)
        self.prev_bingo = deepcopy(self.bingo)
        self.save_file = ""
        self.replaceMode = False

        self.initUI()

    def initUI(self):
        """
        Creates the UI at start-up.
        """
        # Window parameters
        self.setWindowIcon(QIcon("resources/icon.ico"))
        self.setWindowTitle("Bearathon 5")
        self.central_widget = QGroupBox()
        self.bingo_layout = QGridLayout()
        self.central_widget.setLayout(self.bingo_layout)
        self.setCentralWidget(self.central_widget)
        self.createMenuBar()
        self.createToolBar()
        self.showMaximized()

    ###########
    # Menubar #
    ###########

    def createMenuBar(self):
        """
        Menubar builder.
        """
        menuBar = QMenuBar(self)
        
        # Create menus
        fileMenu = QMenu("&File", self)
        editMenu = QMenu("&Edit", self)
        
        # Add menus to menubar
        menuBar.addMenu(fileMenu)
        menuBar.addMenu(editMenu)

        # Create actions
        fileNew = QAction("&New", self)
        fileNew.triggered.connect(self.fileNew)
        fileOpen = QAction("&Open", self)
        fileOpen.triggered.connect(self.fileOpen)
        fileExport = QAction("&Export Objectives List", self)
        fileExport.triggered.connect(self.fileExportList)
        editUndo = QAction("&Undo", self)
        editUndo.triggered.connect(self.editUndo)
        editManageList = QAction("&Manage Objectives List", self)
        editManageList.triggered.connect(self.editManageList)

        # Add actions to menus
        fileMenu.addActions([fileNew,
                             fileOpen,
                             fileExport])
        editMenu.addActions([editUndo,
                             editManageList])

        self.setMenuBar(menuBar)

    def fileNew(self):
        """
        Opens a new bingo from a csv file of items.
        """
        dlg = newBingoSetupDialog()
        if dlg.exec():
            output = dlg.output()
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setWindowTitle("Warning")
            if not output["list_file"]:
                msg.setText("Objectives List File missing!")
                msg.exec()
            elif not output["save_file"]:
                msg.setText("Save File missing!")
                msg.exec()
            elif output["pokemon"] and output["size"] % 2 == 0:
                msg.setText("Pokemon in middle square cannot be checked while size is even!")
                msg.exec()
            else:
                self.save_file = output["save_file"]
                self.bingo = Bingo(output["size"], output["pokemon"], active=True, new=True, list_file=output["list_file"])
                self.prev_bingo = deepcopy(self.bingo)
                self.save()
                self.updateBingoUI()

    def fileOpen(self):
        """
        Opens a bingo from a save file.
        """
        fileName, _ = QFileDialog.getOpenFileName(self, "Open File", "","JSON File (*.json);;All Files (*)")
        if fileName:
            with open(fileName, 'r') as f:
                data = json_load(f)
            try:
                size = int(data["size"])
                pokemon = data["pokemon"]
                grid = data["grid"]
                obj_list = data["list"]
                current_pokemon = data["current_pokemon"]
                pokemon_status = data["pokemon_status"]
                self.bingo = Bingo.fromSave(size, pokemon, grid, obj_list, current_pokemon, pokemon_status)
                self.save_file = fileName
                self.prev_bingo = deepcopy(self.bingo)
                self.updateBingoUI()
            except Exception as e:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Icon.Warning)
                msg.setWindowTitle("Couldn't read file.")
                msg.setText(str(e))
                msg.exec()
    
    def fileExportList(self):
        """
        Opens a file dialog to save the objectives list file.
        """
        fileName, _ = QFileDialog.getSaveFileName(self, "Save File", "","CSV File (*.csv)")
        if fileName:
            self.bingo.export_list(fileName)

    def editUndo(self):
        """
        Reverts to the previous bingo state. (Only 1 previous state gets saved!)
        """
        if self.prev_bingo.active:
            self.bingo = deepcopy(self.prev_bingo)
            self.save()
            self.updateBingoUI()
    
    def editManageList(self):
        """
        Opens a dialog to manage the objectives list.
        """
        if self.bingo.active:
            dlg = manageListDialog(self.bingo.list)
            if dlg.exec():
                self.bingo.list = dlg.output()
                self.updateBingoUI()

    ###########
    # Toolbar #
    ###########

    def createToolBar(self):
        """
        Toolbar Builder.
        """
        toolBar = QToolBar()

        # Create actions
        shuffle = QAction("&Shuffle", self)
        shuffle.triggered.connect(self.toolShuffle)
        replace = QAction("&Replace", self)
        replace.triggered.connect(self.toolReplace)
        new_poke = QAction("&New Pokemon", self)
        new_poke.triggered.connect(self.toolNewPoke)
        wipe = QAction("&Wipe the board", self)
        wipe.triggered.connect(self.toolWipe)
        reset = QAction("&Reset", self)
        reset.triggered.connect(self.toolReset)

        # Add actions to toolbar
        toolBar.addActions([shuffle,
                            replace,
                            new_poke,
                            wipe,
                            reset])

        self.addToolBar(toolBar)
    
    def toolShuffle(self):
        if self.bingo.active:
            self.prev_bingo = deepcopy(self.bingo)
            self.bingo.shuffle()
            self.save()
            self.updateBingoUI()

    def toolReplace(self):
        if self.bingo.active:
            if self.replaceMode:
                self.replaceMode = False
                # visual cue that mode changed
                self.updateBingoUI()
            else:
                self.replaceMode = True
                # visual cue that mode changed
                for row in self.bingo_squares:
                    for square in row:
                        square.setStyleSheet("background-color: red")
                self.bingo_layout.update()

    def toolNewPoke(self):
        if self.bingo.active and self.bingo.pokemon_bool:
            dlg = replaceSquareDialog()
            if dlg.exec():
                self.prev_bingo = deepcopy(self.bingo)
                random, new_poke = dlg.output()
                self.bingo.replace(int(self.bingo.size/2), int(self.bingo.size/2), random, new_poke)
                self.updateBingoUI()

    def toolWipe(self):
        if self.bingo.active:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setWindowTitle("Warning")
            msg.setText("Are you sure you want to wipe the board?")
            msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if msg.exec() == QMessageBox.StandardButton.Yes:
                self.prev_bingo = deepcopy(self.bingo)
                self.bingo.populate()
                self.updateBingoUI()

    def toolReset(self):
        if self.bingo.active:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setWindowTitle("Warning")
            msg.setText("Are you sure you want to reset?\nYou will lose all objective progress.")
            msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if msg.exec() == QMessageBox.StandardButton.Yes:
                self.prev_bingo = deepcopy(self.bingo)
                self.bingo.reset()
                self.updateBingoUI()

    ########
    # Misc #
    ########
                
    def save(self):
        """
        Saves the current file.
        """
        if self.bingo.active:
            bingo_dict = self.bingo.toDict()
            with open(self.save_file, "w") as f:
                json_dump(bingo_dict, f, indent=1)

    def updateBingoUI(self):
        for i in reversed(range(self.bingo_layout.count())):
            item = self.bingo_layout.itemAt(i)
            if item:
                item.widget().setParent(None)
        self.bingo_squares = []
        for i in range(self.bingo.size):
            row = []
            for j in range(self.bingo.size):
                square = QPushButton()
                square.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
                label = QLabel(self.bingo.grid[i][j], square)
                label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                label.setWordWrap(True)
                squareLayout = QHBoxLayout(square)
                squareLayout.addWidget(label)
                square.clicked.connect(self.squarePress)
                if not (self.bingo.pokemon_bool and i == j and i == int(self.bingo.size/2)):
                    if self.bingo.list[self.bingo.grid[i][j]] == 1:
                        square.setStyleSheet("background-color: green")
                    else:
                        square.setStyleSheet("")
                else:
                    if self.bingo.pokemon_status == 1:
                        square.setStyleSheet("background-color: green")
                    else:
                        square.setStyleSheet("")
                self.bingo_layout.addWidget(square, i, j)
                row.append(square)
            self.bingo_squares.append(row)
        self.bingo_layout.update()

    def squarePress(self):
        sender = self.sender()
        for i, row in enumerate(self.bingo_squares):
            for j, square in enumerate(row):
                if sender == square:
                    if self.replaceMode:
                        dlg = replaceSquareDialog()
                        if dlg.exec():
                            self.prev_bingo = deepcopy(self.bingo)
                            random, newGoal = dlg.output()
                            self.bingo.replace(i, j, random, newGoal)
                            self.updateBingoUI()
                        self.replaceMode = False
                    else:
                        if not (self.bingo.pokemon_bool and i == j and i == int(self.bingo.size/2)):
                            if self.bingo.list[self.bingo.grid[i][j]] == 0:
                                self.bingo.list[self.bingo.grid[i][j]] = 1
                                square.setStyleSheet("background-color: green")
                            elif self.bingo.list[self.bingo.grid[i][j]] == 1:
                                self.bingo.list[self.bingo.grid[i][j]] = 0
                                square.setStyleSheet("")
                        else:
                            if self.bingo.pokemon_status == 0:
                                self.bingo.pokemon_status = 1
                                square.setStyleSheet("background-color: green")
                            elif self.bingo.pokemon_status == 1:
                                self.bingo.pokemon_status = 0
                                square.setStyleSheet("")
        self.save()
        self.bingo_layout.update()

##################
# Custom dialogs #
##################

class newBingoSetupDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowIcon(QIcon("resources/icon.ico"))
        self.setWindowTitle("New Bingo Setup")

        buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        layout = QFormLayout(self)

        open = QPushButton("Open", self)
        open.pressed.connect(self.openButton)
        layout.addRow("Import List of Objectives:", open)
        self.list_file = ""
        self.list_file_label = QLabel(self)
        layout.addRow("List of Objectives Location:", self.list_file_label)
        self.bingo_size = QSpinBox(self, minimum=1, singleStep=2, value=5)
        layout.addRow("Bingo Size (x by x):", self.bingo_size)
        self.pokemon = QCheckBox(self)
        self.pokemon.setChecked(True)
        layout.addRow("Pokemon in Middle Square:", self.pokemon)
        save = QPushButton("Save", self)
        save.pressed.connect(self.saveButton)
        layout.addRow("Save Bingo File:", save)
        self.save_file = ""
        self.save_file_label = QLabel(self)
        layout.addRow("Save File Location:", self.save_file_label)
        
        layout.addWidget(buttonBox)

    def openButton(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "THE List File", "","CSV File (*.csv);;Text File (*.txt);;All Files (*)")
        if fileName:
            self.list_file = fileName
            self.list_file_label.setText(fileName)

    def saveButton(self):
        fileName, _ = QFileDialog.getSaveFileName(self, "Save As", "","JSON File (*.json)")
        if fileName:
            root, ext = os_path.splitext(fileName)
            ext = ".json"
            fileName = root + ext
            self.save_file = fileName
            self.save_file_label.setText(fileName)

    def output(self) -> dict:
        return {"list_file": self.list_file,
                "size": self.bingo_size.value(),
                "pokemon": self.pokemon.isChecked(),
                "save_file": self.save_file}
    
class replaceSquareDialog(QDialog):
    def __init__(self) -> None:
        super().__init__()
        
        self.setWindowIcon(QIcon("resources/icon.ico"))
        self.setWindowTitle("Replace")

        buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        layout = QFormLayout(self)

        self.random = QCheckBox(self)
        layout.addRow("Random:", self.random)
        self.newGoal = QLineEdit(self)
        self.newGoal.setEnabled(True)
        layout.addRow("New Objective if not random:", self.newGoal)
        
        layout.addWidget(buttonBox)

    def output(self) -> tuple[bool, str]:
        """
        Returns a bool for random in 1 and new goal if not random in 2.
        """
        return self.random.isChecked(), self.newGoal.text()
    
class manageListDialog(QDialog):
    def __init__(self, obj_list: dict):
        super().__init__()

        self.setWindowIcon(QIcon("resources/icon.ico"))
        self.setWindowTitle("Manage Objectives")

        buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        tabWidget = QTabWidget()
        tabWidget.addTab(self.status_tab(obj_list), "Status")
        tabWidget.addTab(self.add_tab(), "Add")
        tabWidget.addTab(self.remove_tab(), "Remove")

        layout = QVBoxLayout(self)
        layout.addWidget(tabWidget)
        layout.addWidget(buttonBox)

    def status_tab(self, obj_list: dict) -> QWidget:
        form = QWidget()
        self.form_layout = QFormLayout()
        self.form_dict = {}

        for key in obj_list:
            value = QSpinBox(self)
            value.setMinimum(0)
            value.setMaximum(1)
            value.setValue(obj_list[key])
            self.form_dict[key] = value
            self.form_layout.addRow(key, value)
        form.setLayout(self.form_layout)

        scroll = QScrollArea()
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setWidgetResizable(True)
        scroll.setWidget(form)

        searchbar = QLineEdit()
        searchbar.textChanged.connect(self.search_update)

        container = QWidget()
        containerLayout = QVBoxLayout()
        containerLayout.addWidget(searchbar)
        containerLayout.addWidget(scroll)
        container.setLayout(containerLayout)
        return container
    
    def add_tab(self) -> QWidget:
        add_layout = QFormLayout()
        self.new_goal = QLineEdit()
        add_layout.addRow("New Objective:", self.new_goal)
        add_goal = QPushButton("Add")
        add_goal.pressed.connect(self.add_goal)
        add_layout.addRow("", add_goal)
        container = QWidget()
        container.setLayout(add_layout)
        return container
    
    def remove_tab(self) -> QWidget:
        remove_layout = QFormLayout()
        self.remove_goal = QComboBox()
        self.remove_goal.setEditable(True)
        self.remove_goal.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.remove_goal.addItems(self.form_dict.keys())
        remove_layout.addRow("Remove:", self.remove_goal)
        remove = QPushButton("Remove")
        remove.pressed.connect(self.remove)
        remove_layout.addRow("", remove)
        container = QWidget()
        container.setLayout(remove_layout)
        return container

    def search_update(self, text: str):
        for key in self.form_dict:
            for idx in range(self.form_layout.rowCount()):
                widgetItem = self.form_layout.itemAt(idx, QFormLayout.ItemRole.LabelRole)
                if key == widgetItem.widget().text():
                    if text.lower() in key.lower():
                        self.form_layout.setRowVisible(idx, True)
                    else:
                        self.form_layout.setRowVisible(idx, False)

    def add_goal(self):
        if self.new_goal.text():
            value = QSpinBox(self)
            value.setMinimum(0)
            value.setMaximum(1)
            value.setValue(0)
            self.form_dict[self.new_goal.text()] = value
            self.form_layout.addRow(self.new_goal.text(), value)
            self.remove_goal.addItem(self.new_goal.text())
            self.new_goal.clear()
    
    def remove(self):
        if self.remove_goal.currentText():
            if self.remove_goal.currentText() in self.form_dict:
                self.form_layout.removeRow(list(self.form_dict.keys()).index(self.remove_goal.currentText()))
                self.form_dict.pop(self.remove_goal.currentText())
                self.remove_goal.removeItem(self.remove_goal.findText(self.remove_goal.currentText()))
                self.remove_goal.clearEditText()
            else:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Icon.Warning)
                msg.setWindowTitle("Warning")
                msg.setText("Objective not found. Nothing was removed.")
                msg.exec()

    def output(self) -> dict:
        output_dict = {}
        for key in self.form_dict:
            output_dict[key] = self.form_dict[key].value()
        return output_dict