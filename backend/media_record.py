import os
from typing import Iterable, Set

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
        self.media_type: str | None = self.metadata.get("type")
        # self.title refers to the 'total' title. For movies, it's the movie title. For episodes, it's the series title.
        self.title: str | None = self.metadata.get("title")
        self.year: int | None = self.metadata.get("year")

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
    def is_tv_series(media_record_list: Iterable["MediaRecord"]) -> bool:
        return MediaRecord.has_episodes(media_record_list) and not MediaRecord.has_movies(media_record_list)

    @staticmethod
    def get_unique_titles(media_record_list: Iterable["MediaRecord"]) -> Set[str]:
        """
        Returns a set of unique titles from a media_record_list.
        Useful to check the validity of an episode file list, e.g., whether there are multiple tv series.
        """

        # Gather unique series titles; ignore records without a series title.
        return {record.title for record in media_record_list if record.title is not None}

    @staticmethod
    def update_title_for_all_records(title: str, media_record_list: Iterable["MediaRecord"]):
        for media_record in media_record_list:
            media_record.title = title
