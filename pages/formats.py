from PySide6.QtGui import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton, QTabWidget, QLabel

from backend.formats_backend import retrieve_movies_format_from_formats_file, save_new_movies_format_to_formats_file, \
    retrieve_series_format_from_formats_file, save_new_series_format_to_formats_file


class FormatsPage(QWidget):
    """Formats page for users to set what renaming format they want for TV episodes and movies."""

    def __init__(self, parent=None):
        super().__init__(parent)

        formats_page_layout = QVBoxLayout(self)

        # Tab bar for Movies & TV Episodes.
        tab_bar = QTabWidget()
        formats_page_layout.addWidget(tab_bar)

        # Movie tab.
        movie_tab = QWidget()
        movie_tab_layout = QVBoxLayout(movie_tab)

        # Input textbox for users to view and edit their desired movies renaming format.
        movie_line_edit = QLineEdit()
        movie_line_edit.setText(retrieve_movies_format_from_formats_file())
        movie_tab_layout.addWidget(movie_line_edit)

        # Update button for movies format.
        movie_update_button = QPushButton("Update")
        movie_update_button.clicked.connect(lambda: save_new_movies_format_to_formats_file(movie_line_edit.text()))
        movie_tab_layout.addWidget(movie_update_button)

        # Movie format tutorial and examples.
        movie_syntax_label = QLabel("{movie_name} = Title\n"
                                    "{year} = Year\n"
                                    "\nExamples:\n"
                                    "{movie_name} ({year}) \n"
                                    "\tMovieName.2020.ENGLISH.720p.WEBRip.800MB.x264-GalaxyRG.mkv"
                                    " = MovieName (2020)")
        movie_tab_layout.addWidget(movie_syntax_label)

        movie_tab.layout().setAlignment(Qt.AlignmentFlag.AlignTop)

        # Episode tab.
        episode_tab = QWidget()
        episode_tab_layout = QVBoxLayout(episode_tab)

        # Textbox.
        series_line_edit = QLineEdit()
        series_line_edit.setText(retrieve_series_format_from_formats_file())
        episode_tab_layout.addWidget(series_line_edit)

        # Update button for series format.
        series_update_button = QPushButton("Update")
        series_update_button.clicked.connect(lambda:
                                             save_new_series_format_to_formats_file(series_line_edit.text()))
        episode_tab_layout.addWidget(series_update_button)

        # Episode format tutorial and examples.
        episode_syntax_label = QLabel("{series_name} = Title\n"
                                      "{season_number} = Season Number\n"
                                      "{episode_number} = Episode Number\n"
                                      "{episode_title} = Episode Title\n"
                                      "{year} = Year\n"
                                      "\nExamples:\n"
                                      "{series_name} - S{season_number}E{episode_number} - {episode_title}\n"
                                      "\tChernobyl.S01E01.1.23.45.2160p.DTS-HD.MA.5.1.DV.HEVC.REMUX-FraMeSToR.mkv"
                                      " = Chernobyl - S01E01 - 1.23.45.mkv\n")
        episode_tab_layout.addWidget(episode_syntax_label)

        episode_tab.layout().setAlignment(Qt.AlignmentFlag.AlignTop)

        tab_bar.addTab(movie_tab, "Movies")
        tab_bar.addTab(episode_tab, "TV Episodes")
