import os
import sys

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QListWidget, QStackedWidget, QSizePolicy

from pages.core import CorePage
from pages.formats import FormatsPage
from pages.preferences import PreferencesPage


class MainWindow(QMainWindow):
    """Container for different Widgets/Pages with a menu-style list for switching between pages."""

    def __init__(self):
        super().__init__()

        central_layout = QHBoxLayout()

        # Widget (List) that displays clickable tabs that allows for switching pages.
        self.menu = QListWidget()
        self.menu.addItems(["Rename", "Formats", "Settings"])
        self.menu.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        central_layout.addWidget(self.menu)

        # QStackedWidget stores different pages/widgets that can be switched to/from.
        # See: https://doc.qt.io/qt-6/qstackedwidget.html.
        self.pages = QStackedWidget()
        self.pages.addWidget(CorePage())
        self.pages.addWidget(FormatsPage())
        self.pages.addWidget(PreferencesPage())
        self.pages.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
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
        self.setMinimumSize(600, 200)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()

    # If running as a GitHub Actions build check, auto-quit after one second since app is a UI.
    if os.environ.get("CI", "false").lower() == "true":
        QTimer.singleShot(1000, app.quit)

    sys.exit(app.exec())
