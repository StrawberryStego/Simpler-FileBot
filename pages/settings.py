import os.path
import sys

from PySide6.QtCore import Slot, QCoreApplication, QProcess, QUrl
from PySide6.QtGui import QGuiApplication, Qt, QDesktopServices
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QPushButton, QMessageBox, QListWidget, \
    QHBoxLayout, QToolButton, QStyle, QFileDialog, QListWidgetItem

from backend.api_key_config import delete_and_recreate_api_keys_file
from backend.settings_backend import (retrieve_theme_from_settings, save_new_theme_to_settings, add_excluded_folder,
                                      retrieve_excluded_folders, remove_excluded_folder,
                                      delete_and_recreate_settings_file, get_settings_file_path)


def set_color_theme_on_startup():
    """
    Grabs the desired theme from settings and sets the color theme for the UI before other elements are drawn.
    Setting the color theme after elements have been drawn does not work.
    """

    if retrieve_theme_from_settings() == "Light":
        QGuiApplication.styleHints().setColorScheme(Qt.ColorScheme.Light)
    else:
        # Default to 'Dark' otherwise.
        QGuiApplication.styleHints().setColorScheme(Qt.ColorScheme.Dark)


class SettingsPage(QWidget):
    """Settings page for miscellaneous options/settings."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("settings")

        settings_page_layout = QVBoxLayout(self)

        # Theme Selection UI Components.
        theme_label = QLabel("Select Theme:")
        self.theme_options = QComboBox()
        self.theme_options.addItems(["Light", "Dark"])
        if retrieve_theme_from_settings() == "Dark":
            self.theme_options.setCurrentIndex(1)
        self.theme_options.currentIndexChanged.connect(self.on_theme_changed)

        # Folder Exclusion UI Components.
        folder_exclusion_label = QLabel("Folder Exclusions:")
        self.folder_exclusion_list = QListWidget()
        folder_exclusion_button_layout = QHBoxLayout()
        help_button = QToolButton()
        help_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MessageBoxQuestion))
        help_button.setToolTip(
            "Simpler FileBot uses 'guessit' to guess information about your files based on its total path."
            "\nThis allows the guessing library to guess the series name, e.g., /TV Series Name/Season 1/..."
            "\nHowever, there are certain parent folder names that can conflict with that."
            "\n\nThe library guesses the TV name for 'C:/Stuff Ultra/TV Series Name/Season 1/...', as 'Stuff Ultra'."
            "\n\nFolder Exclusions allows you to exclude 'C:/Stuff Ultra/' but retain everything after during guessing."
        )
        help_button.setAutoRaise(True)
        add_folders_button = QPushButton("📁 Add Folder")
        add_folders_button.clicked.connect(self.choose_exclusion_folder)
        delete_folder_button = QPushButton("❌ Delete Folder")
        delete_folder_button.clicked.connect(self.delete_selected_excluded_folder)
        folder_exclusion_button_layout.addWidget(help_button)
        folder_exclusion_button_layout.addWidget(add_folders_button)
        folder_exclusion_button_layout.addWidget(delete_folder_button)

        # Opens the settings folder when clicked.
        open_settings_button = QPushButton("📁 Open Settings Folder")
        open_settings_button.clicked.connect(self.open_settings_folder)

        # Reset Settings UI Components.
        reset_button = QPushButton("Reset All Settings to Default")
        reset_button.clicked.connect(self.reset_settings)

        # Grabs settings from settings.json and displays them to the user on startup.
        set_color_theme_on_startup()
        self.display_excluded_folders_from_settings()

        settings_page_layout.addWidget(theme_label)
        settings_page_layout.addWidget(self.theme_options)
        settings_page_layout.addWidget(folder_exclusion_label)
        settings_page_layout.addWidget(self.folder_exclusion_list)
        settings_page_layout.addLayout(folder_exclusion_button_layout)
        settings_page_layout.addStretch()
        settings_page_layout.addWidget(open_settings_button)
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
                                     "Do you want to reset all settings to defaults?"
                                     "\n\n[This will delete all API keys]",
                                     QMessageBox.StandardButton.Yes,
                                     QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            delete_and_recreate_settings_file()
            delete_and_recreate_api_keys_file()
            self.display_excluded_folders_from_settings()

    @Slot()
    def choose_exclusion_folder(self):
        """
        Allow users to choose an exclusion folder.
        Add it to folder exclusion's QListWidget and save it to settings.json.
        """
        selected_exclusion_folder = QFileDialog.getExistingDirectory(
            self,
            "Select Folder to Exclude",
            "",
            QFileDialog.Option.ShowDirsOnly | QFileDialog.Option.DontResolveSymlinks
        )

        if selected_exclusion_folder:
            add_excluded_folder(selected_exclusion_folder)
            self.display_excluded_folders_from_settings()

    @Slot()
    def delete_selected_excluded_folder(self):
        # Selected items should return one folder since only one QListWidgetItem can be selected at once.
        selected_items = self.folder_exclusion_list.selectedItems()
        if not selected_items:
            return

        for item in selected_items:
            # Grab the actual folder path from the QListWidgetItem.
            folder_path = item.text()
            remove_excluded_folder(folder_path)
            self.display_excluded_folders_from_settings()

    @Slot()
    def open_settings_folder(self):
        settings_folder_path = os.path.dirname(get_settings_file_path())
        QDesktopServices.openUrl(QUrl.fromLocalFile(settings_folder_path))

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

    def display_excluded_folders_from_settings(self):
        """Displays the current excluded folders from settings.json. Old values are removed from the QListWidget."""
        self.folder_exclusion_list.clear()

        for folder in retrieve_excluded_folders():
            self.folder_exclusion_list.addItem(QListWidgetItem(folder))
