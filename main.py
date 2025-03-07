import sys
from PySide6.QtWidgets import QApplication, QWidget


def main():
    app = QApplication(sys.argv)
    main_window = QWidget()
    main_window.show()

    sys.exit(app.exec())

if __name__ == '__main__':
    main()

