from json import dump as json_dump, load as json_load
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import (QMainWindow, QGroupBox, QFileDialog, QMenuBar, QMenu, QFormLayout,
                                QPushButton, QSizePolicy, QGridLayout, QDialog, QDialogButtonBox,
                                QSpinBox, QCheckBox, QLabel, QMessageBox, QToolBar, QVBoxLayout, QLineEdit)
from os import path as os_path


from bingo import Bingo

class App(QMainWindow):
    def __init__(self):
        super().__init__()

        self.bingo = Bingo("", 0, False, False)
        self.save_file = ""
        self.replaceMode = False

        self.initUI()

    def initUI(self):
        """
        Creates the UI at start-up.
        """
        # Window parameters
        self.setWindowIcon(QIcon("resources/icon.png"))
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
        
        # Add menus to menubar
        menuBar.addMenu(fileMenu)

        # Create actions
        fileNew = QAction("&New", self)
        fileNew.triggered.connect(self.fileNew)
        fileOpen = QAction("&Open", self)
        fileOpen.triggered.connect(self.fileOpen)

        # Add actions to menus
        fileMenu.addActions([fileNew,
                             fileOpen])

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
                self.bingo = Bingo(output["list_file"], output["size"], output["pokemon"])
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
                list_file = data["list_file"]
                size = int(data["size"])
                pokemon = data["pokemon"]
                grid = data["grid"]
                grid_status = data["grid_status"]
                self.bingo = Bingo.fromSave(list_file, size, pokemon, grid, grid_status)
                self.save_file = fileName
                self.updateBingoUI()
            except Exception as e:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Icon.Warning)
                msg.setWindowTitle("Couldn't read file.")
                msg.setText(str(e))
                msg.exec()

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

        # Add actions to toolbar
        toolBar.addActions([shuffle,
                            replace,
                            new_poke])

        self.addToolBar(toolBar)
    
    def toolShuffle(self):
        if self.bingo.active:
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
            dlg = replaceSquare()
            if dlg.exec():
                random, new_poke = dlg.output()
                self.bingo.replace(int(self.bingo.size/2), int(self.bingo.size/2), random, new_poke)
                self.updateBingoUI()

    ########
    # Misc #
    ########
                
    def save(self):
        """
        Saves the current file.
        """
        if self.bingo:
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
                square = QPushButton(self.bingo.grid[i][j])
                square.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
                square.clicked.connect(self.squarePress)
                if self.bingo.grid_status[i][j] == 1:
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
                        dlg = replaceSquare()
                        if dlg.exec():
                            random, newGoal = dlg.output()
                            self.bingo.replace(i, j, random, newGoal)
                            self.updateBingoUI()
                        self.replaceMode = False
                    else:
                        if self.bingo.grid_status[i][j] == 0:
                            self.bingo.grid_status[i][j] = 1
                            square.setStyleSheet("background-color: green")
                        elif self.bingo.grid_status[i][j] == 1:
                            self.bingo.grid_status[i][j] = 0
                            square.setStyleSheet("")
        self.save()
        self.bingo_layout.update()

##################
# Custom dialogs #
##################

class newBingoSetupDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowIcon(QIcon("resources/icon.png"))
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
    
class replaceSquare(QDialog):
    def __init__(self) -> None:
        super().__init__()
        
        self.setWindowIcon(QIcon("resources/icon.png"))
        self.setWindowTitle("New Bingo Setup")

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