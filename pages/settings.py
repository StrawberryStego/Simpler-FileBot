from PySide6.QtCore import Slot
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QPushButton, QMessageBox

from backend.settings_backend import get_theme_from_settings, reset_settings_to_default


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

        # Reset Settings UI Components.
        reset_button = QPushButton("Reset All Settings to Default")
        reset_button.clicked.connect(self.reset_settings_and_update_ui)

        self.update_ui_elements_from_settings()

        settings_page_layout.addWidget(title)
        settings_page_layout.addWidget(theme_label)
        settings_page_layout.addWidget(self.theme_options)
        settings_page_layout.addStretch()
        settings_page_layout.addWidget(reset_button)

    @Slot()
    def reset_settings_and_update_ui(self):
        reply = QMessageBox.question(self, "Reset Settings",
                                     "Do you want to reset all settings to defaults?",
                                     QMessageBox.StandardButton.Yes,
                                     QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            reset_settings_to_default()

        self.update_ui_elements_from_settings()

    def update_ui_elements_from_settings(self):
        """Retrieves settings from settings.json and updates UI elements to match."""

        if get_theme_from_settings() == "Light":
            self.theme_options.setCurrentIndex(0)
        else:
            # Default to 'Dark' otherwise.
            self.theme_options.setCurrentIndex(1)
