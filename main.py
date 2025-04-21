import os
import sys

from PySide6.QtCore import QTimer
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QListWidget, QStackedWidget, QSizePolicy

from pages.core import CorePage
from pages.formats import FormatsPage
from pages.preferences import PreferencesPage

# Percentage of the screen's dimensions that various widget sizes should adhere to.
DEFAULT_APP_WIDTH_SCALING = 0.70
DEFAULT_APP_HEIGHT_SCALING = 0.60
MINIMUM_MENU_BAR_WIDTH_SCALING = 0.08


class MainWindow(QMainWindow):
    """Container for different Widgets/Pages with a menu-style list for switching between pages."""

    def __init__(self):
        super().__init__()
        central_layout = QHBoxLayout()
        screen_size_info = QGuiApplication.primaryScreen().availableGeometry()

        # Widget (List) that displays clickable tabs that allows for switching pages.
        self.menu = QListWidget()
        self.menu.addItems(["↔️ Rename", "🟰 Formats", "⚙️ Settings"])
        # Max & 150px is needed so the menu bar does not become miniscule on small-dpi monitors.
        self.menu.setMinimumWidth(max(150, int(screen_size_info.width() * MINIMUM_MENU_BAR_WIDTH_SCALING)))
        self.menu.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)
        central_layout.addWidget(self.menu)

        # QStackedWidget that stores different pages/widgets that can be switched to/from.
        self.pages = QStackedWidget()
        self.pages.addWidget(CorePage())
        self.pages.addWidget(FormatsPage())
        self.pages.addWidget(PreferencesPage())
        self.pages.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)
        central_layout.addWidget(self.pages)

        # Connects signal for when the user clicks on a menu tab to setCurrentIndex()'s slot to change pages.
        self.menu.currentRowChanged.connect(self.pages.setCurrentIndex)
        self.menu.setCurrentRow(0)

        # Package the central_layout into a QWidget container as QMainWindow works with Widgets, not layouts.
        central_widget_container = QWidget()
        central_widget_container.setLayout(central_layout)
        self.setCentralWidget(central_widget_container)

        # Set styles for the page-switching menu.
        self.menu.setStyleSheet("""
        QListWidget {
            font-size: 20pt;
        }
        QListWidget::item {
            margin: 1em;
        }
        """)

        # Additional window setup.
        self.setWindowTitle("Simpler FileBot v0.5")

        # Set the main application to start at a percentage of the screen's size.
        default_screen_width = int(screen_size_info.width() * DEFAULT_APP_WIDTH_SCALING)
        default_screen_height = int(screen_size_info.height() * DEFAULT_APP_HEIGHT_SCALING)
        self.resize(default_screen_width, default_screen_height)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()

    # If running as a GitHub Actions build check, auto-quit after one second since app is a UI.
    if os.environ.get("CI", "false").lower() == "true":
        QTimer.singleShot(1000, app.quit)

    sys.exit(app.exec())
