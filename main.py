import sys

from PySide6.QtWidgets import QApplication

from utils.assets_path_util import resource_path
from views.main_window import MainWindow


def load_stylesheet(file_path: str):
    path = resource_path(file_path)
    with open(path, "r") as file:
        return file.read()


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(load_stylesheet("style.qss"))
    main_window = MainWindow()
    main_window.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
