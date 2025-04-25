import sys

from PySide6.QtCore import Slot, QCoreApplication, QProcess
from PySide6.QtGui import QGuiApplication, Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QPushButton, QMessageBox, QListWidget, \
    QHBoxLayout, QToolButton, QStyle

from backend.settings_backend import (get_theme_from_settings, delete_and_recreate_settings_file,
                                      save_new_theme_to_settings)


def set_color_theme_on_startup():
    """
    Grabs the desired theme from settings and sets the color theme for the UI before other elements are drawn.
    Setting the color theme after elements have been drawn does not work.
    """

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

        # Folder Exclusion UI Components.
        folder_exclusion_label = QLabel("Folder Exclusions:")
        folder_exclusion_list = QListWidget()
        folder_exclusion_button_layout = QHBoxLayout()
        help_button = QToolButton()
        help_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MessageBoxQuestion))
        help_button.setToolTip(
            "Simpler FileBot uses a library to guess information about your files base on its total path."
            "\nThis allows the guessing library to guess the series name, e.g., /TV Series Name/Season 1/..."
            "\nHowever, there are certain parent folder names that can conflict with that."
            "\n\nThe library guesses the TV name for 'C:/Stuff Ultra/TV Series Name/Season 1/...', as 'Stuff Ultra'."
            "\n\nFolder Exclusions allows you to exclude 'C:/Stuff Ultra/' during guessing."
        )
        help_button.setAutoRaise(True)
        add_folders_button = QPushButton("📁 Add Folder(s)")
        delete_folder_button = QPushButton("Delete Folder")
        folder_exclusion_button_layout.addWidget(help_button)
        folder_exclusion_button_layout.addWidget(add_folders_button)
        folder_exclusion_button_layout.addWidget(delete_folder_button)

        # Reset Settings UI Components.
        reset_button = QPushButton("Reset All Settings to Default")
        reset_button.clicked.connect(self.reset_settings)

        set_color_theme_on_startup()

        settings_page_layout.addWidget(title)
        settings_page_layout.addWidget(theme_label)
        settings_page_layout.addWidget(self.theme_options)
        settings_page_layout.addWidget(folder_exclusion_label)
        settings_page_layout.addWidget(folder_exclusion_list)
        settings_page_layout.addLayout(folder_exclusion_button_layout)
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
