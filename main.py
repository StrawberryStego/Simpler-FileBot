#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10,<3.13"
# dependencies = [
#   "PySide6==6.9.0",
#   "shiboken6==6.9.0",
#   "guessit==3.8.0",
#   "pytest==8.3.5",
#   "pytest-qt==4.4.0",
#   "platformdirs==4.3.7",
#   "python-tvmaze==1.0.5",
#   "tmdbsimple==2.9.1",
#   "omdb==0.10.1",
# ]
# ///

import os
import sys
from pathlib import Path


def is_crostini():
    """Detect if running in ChromeOS Crostini environment."""
    # Check for Crostini-specific environment variables
    if os.environ.get("SOMMELIER_VERSION"):
        return True

    # Check for cros-container-guest-tools package
    if Path("/etc/apt/sources.list.d/cros.list").exists():
        return True

    # Check for garcon (Crostini's container manager)
    if Path("/opt/google/cros-containers").exists():
        return True

    return False


def check_crostini_dependencies():
    """Check if required X11 dependencies are installed on Crostini."""
    try:
        import subprocess

        result = subprocess.run(
            ["dpkg", "-l", "libxcb-cursor0"], capture_output=True, text=True
        )
        return result.returncode == 0
    except Exception:
        return False


# Apply Crostini-specific fixes
if is_crostini():
    if not check_crostini_dependencies():
        print("\n" + "=" * 70)
        print("WARNING: Running on ChromeOS Crostini with missing dependencies")
        print("=" * 70)
        print("\nTo fix Qt/Wayland issues, please install required packages:\n")
        print("sudo apt update")
        print("sudo apt install libxcb-cursor0 libxcb-icccm4 libxcb-image0 \\")
        print("    libxcb-keysyms1 libxcb-randr0 libxcb-render-util0 \\")
        print("    libxcb-xfixes0 libxcb-xinerama0 libxcb-xkb1 libxkbcommon-x11-0")
        print("\n" + "=" * 70 + "\n")

        response = input("Continue anyway? (y/n): ")
        if response.lower() != "y":
            sys.exit(1)

    # Force X11 mode on Crostini
    os.environ["QT_QPA_PLATFORM"] = "xcb"
    print("Detected ChromeOS Crostini - using X11 mode for better stability")

from PySide6.QtCore import QTimer
from PySide6.QtGui import QGuiApplication, QIcon, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QListWidget,
    QMainWindow,
    QSizePolicy,
    QStackedWidget,
    QWidget,
)

from pages.core.core import CorePage
from pages.formats import FormatsPage
from pages.settings import SettingsPage

# Percentage of the screen's dimensions that various widget sizes should adhere to.
DEFAULT_APP_WIDTH_SCALING = 0.70
DEFAULT_APP_HEIGHT_SCALING = 0.60


class MainWindow(QMainWindow):
    """Container for different Widgets/Pages with a menu-style list for switching between pages."""

    def __init__(self):
        super().__init__()
        central_layout = QHBoxLayout()
        screen_size_info = QGuiApplication.primaryScreen().availableGeometry()

        # Widget (List) that displays clickable tabs that allows for switching pages.
        self.menu = QListWidget()
        self.menu.addItems(["🖋  Rename", "💾  Formats", "⚙️  Settings"])
        central_layout.addWidget(self.menu)

        # QStackedWidget that stores different pages/widgets that can be switched to/from.
        self.pages = QStackedWidget()
        self.pages.addWidget(CorePage())
        self.pages.addWidget(FormatsPage())
        self.pages.addWidget(SettingsPage())
        self.pages.setSizePolicy(
            QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding
        )
        central_layout.addWidget(self.pages)

        # Connects signal for when the user clicks on a menu tab to setCurrentIndex()'s slot to change pages.
        self.menu.currentRowChanged.connect(self.pages.setCurrentIndex)
        self.menu.setCurrentRow(0)

        # Package the central_layout into a QWidget container as QMainWindow works with Widgets, not layouts.
        central_widget_container = QWidget()
        central_widget_container.setLayout(central_layout)
        self.setCentralWidget(central_widget_container)

        # Set style identifier for the page-switching menu.
        self.menu.setObjectName("menu")
        # Enforce a minimum size limit for the menu. Otherwise, it'll shrink past the text.
        menu_items_width = self.menu.sizeHintForColumn(0)
        self.menu.setMinimumWidth(
            menu_items_width + 15
        )  # Add extra padding on a menu item for QoL.
        self.menu.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        # Additional window setup.
        self.setWindowTitle("Simpler FileBot v1.5.2")
        self.setWindowIcon(QIcon(QPixmap("resources/Alternative App Logo.png")))

        # Set the main application to start at a percentage of the screen's size.
        default_screen_width = int(screen_size_info.width() * DEFAULT_APP_WIDTH_SCALING)
        default_screen_height = int(
            screen_size_info.height() * DEFAULT_APP_HEIGHT_SCALING
        )
        self.resize(default_screen_width, default_screen_height)


def apply_stylesheet(application: QApplication, qss_path: str):
    with Path(qss_path).open("r", encoding="utf-8") as style_file:
        application.setStyleSheet(style_file.read())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    apply_stylesheet(app, "styles/default.qss")
    main_window = MainWindow()
    main_window.show()

    # If running as a GitHub Actions build check, auto-quit after one second since app is a UI.
    if os.environ.get("CI", "false").lower() == "true":
        QTimer.singleShot(1000, app.quit)

    sys.exit(app.exec())
