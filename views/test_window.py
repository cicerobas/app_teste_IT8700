from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget

from controllers.test_controller import TestController, TestState
from models.test_file_model import TestData
from views.result_tab_view import TestResultTabView
from views.steps_tab_view import StepsTabView
from views.test_run_tab_view import TestRunTabView


class TestWindow(QWidget):
    def __init__(self, test_data: TestData, parent: QWidget):
        super().__init__()
        self.test_data = test_data
        self.parent_window = parent
        self.test_controller = TestController(self.test_data)

        self.setWindowTitle("CEBRA IT8700")

        # Signals
        self.test_controller.state_changed.connect(self._toggle_enabled_tabs)

        # Components
        self.tabs = QTabWidget()
        self.test_run_tab = TestRunTabView(self.test_data, self.test_controller)
        self.steps_tab = StepsTabView(self.test_data, self.test_controller)
        self.result_tab = TestResultTabView(self.test_controller)

        self.setLayout(self._setup_layout())

    @Slot()
    def _toggle_enabled_tabs(self):
        disable_tabs_states = [TestState.RUNNING, TestState.PAUSED, TestState.WAITKEY, TestState.NONE]
        enable = self.test_controller.state not in disable_tabs_states
        for index in range(self.tabs.count()):
            if index != 0:
                self.tabs.setTabEnabled(index, enable)

    def _setup_layout(self) -> QVBoxLayout:
        self.tabs.addTab(self.test_run_tab, "RUN")
        self.tabs.addTab(self.steps_tab, "STEPS")
        self.tabs.addTab(self.result_tab, "RESULT")

        v_main_layout = QVBoxLayout()
        v_main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        v_main_layout.addSpacing(10)
        v_main_layout.addWidget(self.tabs)

        return v_main_layout

    def closeEvent(self, event: QCloseEvent) -> None:
        if self.test_controller.monitoring_worker is not None:
            self.test_controller.monitoring_worker.stop()
        self.test_controller.reset_setup()
        self.parent_window.show()
        event.accept()
