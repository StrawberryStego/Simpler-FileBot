from PySide6.QtGui import QFont, QIntValidator, Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTabWidget


class FormatsPage(QWidget):
    """Formats page for users to set what renaming format they want for TV episodes and movies."""

    def __init__(self, parent=None):
        super().__init__(parent)

        formats_page_layout = QVBoxLayout(self)

        # Tab bar for Movies, TV Episodes
        tab_bar = QTabWidget()
        formats_page_layout.addWidget(tab_bar)

        # Movie Tab
        movie_tab = QWidget()
        tab_bar.addTab(movie_tab, "Movies")

        episode_tab = QWidget()
        tab_bar.addTab(episode_tab, "TV Episodes")




