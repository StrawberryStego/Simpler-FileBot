import os
from typing import Iterable

from guessit import guessit

from backend.settings_backend import retrieve_excluded_folders


def retrieve_all_parent_prefixes(folder_path: str) -> set[str]:
    """
    Return the path itself plus every parent directory, all normalized.
    Example: C:/Stuff/Movies  ➜  {'C:\\Stuff\\Movies', 'C:\\Stuff'}
    """
    prefixes: set[str] = set()
    current_folder = os.path.normpath(folder_path).rstrip(os.sep)
    while current_folder and current_folder not in prefixes:
        prefixes.add(current_folder)
        parent = os.path.dirname(current_folder)

        # Reached the drive root. Break out of while loop. No need to add the drive root to prefixes.
        if parent == current_folder:
            break

        current_folder = parent

    return prefixes


def remove_excluded_folders_from_file_path(file_path: str) -> str:
    """
    Strip all excluded folder(s) [strs returned by get_excluded_folders()] from a file path.
    If no match is found the original path is returned.

    Example
    -------
    excluded_folders = ["C:/Stuff/"]
    file_path = "C:/Stuff/Show Name/Season 1/E01.mkv"
    → "Show Name/Season 1/E01.mkv"
    """
    excluded_folders: list[str] = retrieve_excluded_folders()

    # Return the file_path if there are no excluded folders.
    if len(excluded_folders) == 0:
        return file_path

    prefixes: set[str] = set()
    for folder in excluded_folders:
        # Add all parent folder prefixes to prefixes.
        prefixes.update(retrieve_all_parent_prefixes(folder))

    # Normalize OS specific syntax.
    normalized_file_path = os.path.normpath(file_path)

    # Sort the prefixes from longest to shortest so the most-specific prefix is tried first.
    for prefix in sorted(prefixes, key=len, reverse=True):
        if normalized_file_path.lower().startswith(prefix.lower()):
            # Remove the prefix and any leading separator that follows it.
            cleaned_path = normalized_file_path[len(prefix):].lstrip(os.sep)
            # Return the cleaned path after changing to forward slashes for an OS-agnostic result.
            return cleaned_path.replace(os.sep, "/") if cleaned_path else ""

    return file_path


class MediaRecord:
    """Object that contains metadata about a file... more specifically, information about the filename."""

    def __init__(self, file_path: str):
        self.full_file_path = file_path
        # Only include the filename, not the full path, e.g., C:/Folder/File.mp4 -> File.mp4.
        # Here, os is used as it handles different os' path conventions well.
        self.file_name = os.path.basename(file_path)

        # Remove excluded folders from guessit matching consideration, i.e., clean the file_path.
        self.metadata: dict = guessit(remove_excluded_folders_from_file_path(file_path))

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
    def get_unique_titles(media_record_list: Iterable["MediaRecord"]) -> set[str]:
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
