from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel


class PreferencesPage(QWidget):
    """Settings page for miscellaneous options/settings."""

    def __init__(self, parent=None):
        super().__init__(parent)

        preferences_page_layout = QVBoxLayout(self)

        title = QLabel("Welcome to the Preferences Page!")

        preferences_page_layout.addWidget(title)
