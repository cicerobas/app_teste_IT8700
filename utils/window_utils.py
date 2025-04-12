from PySide6.QtWidgets import QApplication, QMessageBox


def center_window(window) -> None:
    screen = QApplication.primaryScreen()
    screen_geometry = screen.availableGeometry()
    screen_center = screen_geometry.center()
    window_geometry = window.frameGeometry()
    window_geometry.moveCenter(screen_center)
    window.move(window_geometry.topLeft())


def show_custom_dialog(text: str, message_type: QMessageBox.Icon) -> None:
    dialog = QMessageBox()
    dialog.setWindowTitle(
        "INFO" if message_type == QMessageBox.Icon.Information else "ERROR"
    )
    dialog.setText(text)
    dialog.setStandardButtons(
        QMessageBox.StandardButton.Ok
        if message_type == QMessageBox.Icon.Information
        else QMessageBox.StandardButton.Close
    )
    dialog.setIcon(message_type)
    dialog.exec()
