from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel


class FormatsPage(QWidget):
    """Formats page for users to set what renaming format they want for TV episodes and movies."""

    def __init__(self, parent=None):
        super().__init__(parent)

        formats_page_layout = QVBoxLayout(self)

        title = QLabel("Welcome to the Formats Page!")

        formats_page_layout.addWidget(title)
