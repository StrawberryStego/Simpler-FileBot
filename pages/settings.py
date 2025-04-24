from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel


class SettingsPage(QWidget):
    """Settings page for miscellaneous options/settings."""

    def __init__(self, parent=None):
        super().__init__(parent)

        preferences_page_layout = QVBoxLayout(self)

        title = QLabel("Welcome to the Settings Page!")

        preferences_page_layout.addWidget(title)
