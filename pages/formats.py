from PySide6.QtGui import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton, QTabWidget, QLabel


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
        movie_tab_layout = QVBoxLayout(movie_tab)

        # Textbox
        self.line_edit = QLineEdit()
        self.line_edit.setPlaceholderText("Enter format here")
        movie_tab_layout.addWidget(self.line_edit)

        # Update button
        self.update_button = QPushButton("Update")
        movie_tab_layout.addWidget(self.update_button)

        # Syntax Label
        self.syntax_label = QLabel("{movie_name} = Title\n"
                                   "{year} = Year\n"
                                   "\nExamples:\n"
                                   "{movie_name} ({year}) \n"
                                   "\tMovieName.2020.ENGLISH.720p.WEBRip.800MB.x264-GalaxyRG.mkv"
                                   " = MovieName (2020)")
        movie_tab_layout.addWidget(self.syntax_label)

        movie_tab.layout().setAlignment(Qt.AlignmentFlag.AlignTop)
        tab_bar.addTab(movie_tab, "Movies")

        # Episode Tab
        episode_tab = QWidget()
        episode_tab_layout = QVBoxLayout(episode_tab)

        # Textbox
        self.line_edit = QLineEdit()
        self.line_edit.setPlaceholderText("Enter format here")
        episode_tab_layout.addWidget(self.line_edit)

        # Update button
        self.update_button = QPushButton("Update")
        episode_tab_layout.addWidget(self.update_button)

        # Syntax Label
        self.syntax_label = QLabel("{series_name} = Title\n"
                                   "{season_number} = Season Number\n"
                                   "{episode_number} = Episode Number\n"
                                   "{episode_title} = Episode Title\n"
                                   "{year} = Year\n"
                                   "\nExamples:\n"
                                   "{{series_name} - {season_number}{episode_number} - {episode_title}}\n"
                                   "\tChernobyl.S01E01.1.23.45.2160p.DTS-HD.MA.5.1.DV.HEVC.REMUX-FraMeSToR.mkv"
                                   " = Chernobyl - S01E01 - 1.23.45.mkv\n")
        episode_tab_layout.addWidget(self.syntax_label)

        episode_tab.layout().setAlignment(Qt.AlignmentFlag.AlignTop)
        tab_bar.addTab(episode_tab, "TV Episodes")
