from PySide6.QtWidgets import QApplication


def center_window(window) -> None:
    screen = QApplication.primaryScreen()
    screen_geometry = screen.availableGeometry()
    screen_center = screen_geometry.center()
    window_geometry = window.frameGeometry()
    window_geometry.moveCenter(screen_center)
    window.move(window_geometry.topLeft())