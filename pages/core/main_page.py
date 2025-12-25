from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout

from pages.core.core_renamer_widget import CoreRenamerWidget
from pages.core.core_toolbar import CoreToolBar


class MainPage(QMainWindow):
    """Main container that hosts the renaming widget and toolbar widget."""

    def __init__(self, parent=None):
        super().__init__(parent)
        renamer_widget = CoreRenamerWidget()
        toolbar_widget = CoreToolBar(renamer_widget.left_box, renamer_widget.right_box)

        # Combine all CorePage components into one QWidget().
        central_widget = QWidget()
        central_widget_layout = QVBoxLayout(central_widget)
        central_widget_layout.addWidget(renamer_widget)
        central_widget_layout.addWidget(toolbar_widget)
        self.setCentralWidget(central_widget)
