import os
from typing import Iterable

from guessit import guessit


class MediaRecord:
    """Object that contains metadata about a file... more specifically, information about the filename."""

    def __init__(self, file_path: str):
        self.full_file_path = file_path
        # Only include the filename, not the full path, e.g., C:/Folder/File.mp4 -> File.mp4.
        # Here, os is used as it handles different os' path conventions well.
        self.file_name = os.path.basename(file_path)

        self.metadata: dict = guessit(file_path)

        # Setting commonly used values, otherwise, get from metadata.
        self.media_type = self.metadata.get("type")
        self.title = self.metadata.get("title")
        self.year = self.metadata.get("year")

    def __str__(self):
        return self.file_name

    def __repr__(self):
        return self.full_file_path

    @staticmethod
    def has_movies(media_record_list: Iterable["MediaRecord"]) -> bool:
        return any(record.media_type == "movie" for record in media_record_list)

    @staticmethod
    def has_episodes(media_record_list: Iterable["MediaRecord"]) -> bool:
        return any(record.media_type == "episode" for record in media_record_list)

    @staticmethod
    def all_have_titles(media_record_list: Iterable["MediaRecord"]) -> bool:
        """
        Returns True if every MediaRecord in the iterable has a title.
        For episodes, 'title' refers to the series name... 'episode_title' refers to the name of the episode.
        """
        return all(record.title is not None for record in media_record_list)
