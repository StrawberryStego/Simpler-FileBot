from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
import os


class PreferencesPage(QWidget):
    """Preferences page for miscellaneous options/settings."""

    def __init__(self, parent=None):
        super().__init__(parent)

        preferences_page_layout = QVBoxLayout(self)

        title = QLabel("Welcome to the Preferences Page!")
        
        location = os.method + "/Simpler Filebot/settings.json"

        preferences_page_layout.addWidget(title)
