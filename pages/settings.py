import sys

from PySide6.QtCore import Slot, QCoreApplication, QProcess
from PySide6.QtGui import QGuiApplication, Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QPushButton, QMessageBox

from backend.settings_backend import (get_theme_from_settings, delete_and_recreate_settings_file,
                                      save_new_theme_to_settings)


def set_ui_elements_from_settings():
    """Retrieves settings from settings.json and sets UI elements to match."""

    if get_theme_from_settings() == "Light":
        QGuiApplication.styleHints().setColorScheme(Qt.ColorScheme.Light)
    else:
        # Default to 'Dark' otherwise.
        QGuiApplication.styleHints().setColorScheme(Qt.ColorScheme.Dark)


class SettingsPage(QWidget):
    """Settings page for miscellaneous options/settings."""

    def __init__(self, parent=None):
        super().__init__(parent)

        settings_page_layout = QVBoxLayout(self)

        title = QLabel("Settings")

        # Theme Selection UI Components.
        theme_label = QLabel("Select Theme:")
        self.theme_options = QComboBox()
        self.theme_options.addItems(["Light", "Dark"])
        if get_theme_from_settings() == "Dark":
            self.theme_options.setCurrentIndex(1)
        self.theme_options.currentIndexChanged.connect(self.on_theme_changed)

        # Reset Settings UI Components.
        reset_button = QPushButton("Reset All Settings to Default")
        reset_button.clicked.connect(self.reset_settings)

        set_ui_elements_from_settings()

        settings_page_layout.addWidget(title)
        settings_page_layout.addWidget(theme_label)
        settings_page_layout.addWidget(self.theme_options)
        settings_page_layout.addStretch()
        settings_page_layout.addWidget(reset_button)

    @Slot(int)
    def on_theme_changed(self, index: int):
        """
        Only save the theme change to settings.json.
        Changing the color scheme after UI elements are built does not work!
        """

        if index == 0:
            save_new_theme_to_settings(Qt.ColorScheme.Light)
        elif index == 1:
            save_new_theme_to_settings(Qt.ColorScheme.Dark)

        # Notify the user to restart the application for changes.
        self.ask_restart()

    @Slot()
    def reset_settings(self):
        reply = QMessageBox.question(self, "Reset Settings",
                                     "Do you want to reset all settings to defaults?",
                                     QMessageBox.StandardButton.Yes,
                                     QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            delete_and_recreate_settings_file()

    def ask_restart(self):
        msg = QMessageBox(self)
        msg.setWindowTitle("Restart Required")
        msg.setText("Please restart the application to apply changes!")
        restart_button = msg.addButton("Restart now", QMessageBox.ButtonRole.AcceptRole)
        msg.addButton("Later", QMessageBox.ButtonRole.RejectRole)
        msg.exec()

        if msg.clickedButton() is restart_button:
            # Restart the application for the user.
            QCoreApplication.quit()
            QProcess.startDetached(sys.executable, sys.argv)
