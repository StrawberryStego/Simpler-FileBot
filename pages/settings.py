from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QPushButton

from backend.settings_backend import get_theme_from_settings


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

        # Reset Settings UI Components.
        reset_button = QPushButton("Reset All Settings to Default")

        settings_page_layout.addWidget(title)
        settings_page_layout.addWidget(theme_label)
        settings_page_layout.addWidget(self.theme_options)
        settings_page_layout.addStretch()
        settings_page_layout.addWidget(reset_button)
