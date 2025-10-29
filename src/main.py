from PySide6.QtWidgets import QApplication
from sys import exit, argv

from ui import App

if __name__ == "__main__":
    app = QApplication(argv)
    window = App()
    exit(app.exec())