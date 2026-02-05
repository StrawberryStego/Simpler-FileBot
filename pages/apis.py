import textwrap
from PySide6.QtGui import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton, QTabWidget, QTextBrowser, QLabel

from backend.api_key_config import (
    retrieve_the_movie_db_key,
    retrieve_omdb_key,
    save_new_the_movie_db_key,
    save_new_omdb_key
)


class ApisPage(QWidget):
    """Page for users to configure their API keys for external metadata providers."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("apis")

        api_page_layout = QVBoxLayout(self)

        # Tab bar for different API services.
        tab_bar = QTabWidget()
        api_page_layout.addWidget(tab_bar)

        # --- The MovieDB Tab ---
        tmdb_tab = QWidget()
        tmdb_layout = QVBoxLayout(tmdb_tab)

        tmdb_layout.addWidget(QLabel("The MovieDB API Key (v3 auth):"))
        self.tmdb_line_edit = QLineEdit()
        self.tmdb_line_edit.setPlaceholderText(
            "Enter your TMDB API key here...")
        self.tmdb_line_edit.setText(retrieve_the_movie_db_key())
        tmdb_layout.addWidget(self.tmdb_line_edit)

        tmdb_update_button = QPushButton("Update TMDB Key")
        tmdb_update_button.clicked.connect(self.save_tmdb_key)
        tmdb_layout.addWidget(tmdb_update_button)

        tmdb_info = QTextBrowser()
        tmdb_info.setOpenExternalLinks(True)
        tmdb_info.setMarkdown(textwrap.dedent("""
            You can obtain your API key by creating an account at 
            [themoviedb.org](https://www.themoviedb.org/settings/api).
        """))
        tmdb_layout.addWidget(tmdb_info)
        tmdb_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # --- OMDB Tab ---
        omdb_tab = QWidget()
        omdb_layout = QVBoxLayout(omdb_tab)

        omdb_layout.addWidget(QLabel("OMDB API Key:"))
        self.omdb_line_edit = QLineEdit()
        self.omdb_line_edit.setPlaceholderText(
            "Enter your OMDB API key here...")
        self.omdb_line_edit.setText(retrieve_omdb_key())
        omdb_layout.addWidget(self.omdb_line_edit)

        omdb_update_button = QPushButton("Update OMDB Key")
        omdb_update_button.clicked.connect(self.save_omdb_key)
        omdb_layout.addWidget(omdb_update_button)

        omdb_info = QTextBrowser()
        omdb_info.setOpenExternalLinks(True)
        omdb_info.setMarkdown(textwrap.dedent("""
            You can request an API key at 
            [omdbapi.com](https://www.omdbapi.com/apikey.aspx).
            <br/><br/>
            **Note:** Free tier keys have daily request limits.
        """))
        omdb_layout.addWidget(omdb_info)
        omdb_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Add tabs to the tab widget
        tab_bar.addTab(tmdb_tab, "The MovieDB")
        tab_bar.addTab(omdb_tab, "OMDB")

    def save_tmdb_key(self):
        """Retrieves the text from the TMDB field and saves it via backend."""
        new_key = self.tmdb_line_edit.text().strip()
        save_new_the_movie_db_key(new_key)

    def save_omdb_key(self):
        """Retrieves the text from the OMDB field and saves it via backend."""
        new_key = self.omdb_line_edit.text().strip()
        save_new_omdb_key(new_key)
