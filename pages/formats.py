from PySide6.QtGui import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton, QTabWidget, QLabel

from backend.formats_backend import read_formats_file, initialize_formats_file, update_format


class FormatsPage(QWidget):
    """Formats page for users to set what renaming format they want for TV episodes and movies."""

    def __init__(self, parent=None):
        super().__init__(parent)
        initialize_formats_file()

        formats_page_layout = QVBoxLayout(self)

        # Tab bar for Movies, TV Episodes.
        tab_bar = QTabWidget()
        formats_page_layout.addWidget(tab_bar)

        # Movie tab.
        movie_tab = QWidget()
        movie_tab_layout = QVBoxLayout(movie_tab)

        # Textbox.
        self.movie_line_edit = QLineEdit()
        self.movie_line_edit.setPlaceholderText("Enter format here")
        movie_format = read_formats_file()
        self.movie_line_edit.setText(movie_format['movie_format'])
        movie_tab_layout.addWidget(self.movie_line_edit)

        # Update button.
        self.movie_update_button = QPushButton("Update")
        self.movie_update_button.clicked.connect(lambda: update_format("movie_format", self.movie_line_edit.text()))
        movie_tab_layout.addWidget(self.movie_update_button)

        # Syntax label.
        self.syntax_label = QLabel("{movie_name} = Title\n"
                                   "{year} = Year\n"
                                   "\nExamples:\n"
                                   "{movie_name} ({year}) \n"
                                   "\tMovieName.2020.ENGLISH.720p.WEBRip.800MB.x264-GalaxyRG.mkv"
                                   " = MovieName (2020)")
        movie_tab_layout.addWidget(self.syntax_label)

        movie_tab.layout().setAlignment(Qt.AlignmentFlag.AlignTop)
        tab_bar.addTab(movie_tab, "Movies")

        # Episode tab.
        episode_tab = QWidget()
        episode_tab_layout = QVBoxLayout(episode_tab)

        # Textbox.
        self.series_line_edit = QLineEdit()
        self.series_line_edit.setPlaceholderText("Enter format here")
        series_format = read_formats_file()
        self.series_line_edit.setText(series_format['series_format'])
        episode_tab_layout.addWidget(self.series_line_edit)

        # Update button.
        self.series_update_button = QPushButton("Update")
        self.series_update_button.clicked.connect(lambda: update_format("series_format", self.series_line_edit.text()))
        episode_tab_layout.addWidget(self.series_update_button)

        # Syntax label.
        self.syntax_label = QLabel("{series_name} = Title\n"
                                   "{season_number} = Season Number\n"
                                   "{episode_number} = Episode Number\n"
                                   "{episode_title} = Episode Title\n"
                                   "{year} = Year\n"
                                   "\nExamples:\n"
                                   "{{series_name} - S{season_number}E{episode_number} - {episode_title}}\n"
                                   "\tChernobyl.S01E01.1.23.45.2160p.DTS-HD.MA.5.1.DV.HEVC.REMUX-FraMeSToR.mkv"
                                   " = Chernobyl - S01E01 - 1.23.45.mkv\n")
        episode_tab_layout.addWidget(self.syntax_label)

        episode_tab.layout().setAlignment(Qt.AlignmentFlag.AlignTop)
        tab_bar.addTab(episode_tab, "TV Episodes")
