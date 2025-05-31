import os
from pathlib import Path
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
        self.title: str | None = None
        raw_title: str | list | None = self.metadata.get("title")
        # If there were multiple titles found, just join them together with a space.
        if isinstance(raw_title, list):
            self.title = " ".join(map(str, raw_title))
        else:
            self.title = raw_title

        self.year: int | None = self.metadata.get("year")

        # Attempt to fill in 'season' or 'episode' if missing (This should not affect movies).
        self._enrich_metadata_via_file_name()

        # Store the container from the original filename.
        self.container: str = Path(file_path).suffix.lstrip(".")

    def _enrich_metadata_via_file_name(self):
        """
        There are edge cases where the name of the folder (Which is used in guessing metadata) stops the
        episode number or season number of a series episode from being parsed correctly.

        This method attempts to analyze the metadata for a series episode using only the file name if
        'season' or 'episode' is missing from the MediaRecord and fills them in."""
        file_name_metadata: dict = guessit(self.file_name)

        if self.metadata.get("season") is None:
            if file_name_metadata.get("season") is not None:
                self.metadata["season"] = file_name_metadata.get("season")

        if self.metadata.get("episode") is None:
            if file_name_metadata.get("episode") is not None:
                self.metadata["episode"] = file_name_metadata.get("episode")

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

    @staticmethod
    def update_year_for_all_records(year: str, media_record_list: Iterable["MediaRecord"]):
        # Validate that the input string can be converted to an int.
        try:
            int_year = int(year.strip())
        except (ValueError, TypeError, AttributeError):
            return  # Input isn't an int‑like string; leave records untouched.

        for media_record in media_record_list:
            media_record.year = int_year

    @staticmethod
    def get_all_season_numbers(media_record_list: Iterable["MediaRecord"]) -> set[int]:
        season_numbers = {media_record.metadata.get("season") for media_record in media_record_list
                          if media_record.metadata.get("season") is not None}

        if len(season_numbers) == 0:
            # If no season numbers are found, default to season 1.
            return {1}

        return season_numbers
