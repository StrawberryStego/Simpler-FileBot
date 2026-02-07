import os
import shutil

from backend.formats_backend import retrieve_series_format_from_formats_file, retrieve_movies_format_from_formats_file
from backend.media_record import MediaRecord
from databases.database import Database


def create_formatted_title(format_template: str, context: dict) -> str:
    """
    Create a formatted title by substituting context values into a format_template string.
    Context values correspond to the supported syntax labeled in the 'Formats' page.
    """

    # Missing values are replaced with {None} so the file name can be marked by the UI.
    normalized_context = {key: ("{None}" if value is None else value) for key, value in context.items()}

    # Returns a formatted title. The context is passed as keyword arguments,
    # instead of positional arguments, to accurately map the context info to the format.
    return format_template.format(**normalized_context)


def match_titles_using_db_and_format(database: Database) -> list[str]:
    """Match each MediaRecord in the database with a correctly formatted file name using the database."""

    formatted_titles = []
    media_records: list[MediaRecord] = database.media_records

    matched_titles = database.retrieve_media_titles_from_db()
    matched_years = database.retrieve_media_years_from_db()

    for i, media_record in enumerate(media_records):
        if database.is_tv_series:
            # Unformatted numbers.
            raw_season_number = media_record.metadata.get("season", 1)
            raw_episode_number: str | None = None

            # guessit might return a list of episode numbers, e.g., S01E10-E11. Just pick the first episode.
            raw_episode_metadata: list = media_record.metadata.get("episode")

            if isinstance(raw_episode_metadata, list) and len(raw_episode_metadata) > 0:
                raw_episode_number = raw_episode_metadata[0]
            else:
                raw_episode_number = str(raw_episode_metadata)

            series_context: dict = {
                "series_name": media_record.title,
                "year": matched_years[i],
                "season_number": f"{int(raw_season_number):02d}" if raw_season_number is not None else None,
                "episode_number": f"{int(raw_episode_number):02d}" if raw_episode_number is not None else None,
                "episode_title": matched_titles[i]
            }

            series_format = retrieve_series_format_from_formats_file()

            formatted_title = create_formatted_title(series_format, series_context)
            formatted_titles.append(f"{formatted_title}.{media_record.container}")
        else:
            movie_context: dict = {
                "movie_name": matched_titles[i],
                "year": matched_years[i]
            }

            movie_format = retrieve_movies_format_from_formats_file()

            formatted_title = create_formatted_title(movie_format, movie_context)
            formatted_titles.append(f"{formatted_title}.{media_record.container}")

    return formatted_titles


def get_invalid_file_names_and_fixes(file_names: list[str]) -> dict[str, str]:
    """
    Check a list of file paths for illegal characters.
    Returns a dictionary mapping original invalid paths to suggested clean paths.
    """
    invalid_files = {}
    # Characters forbidden in both directory paths and filenames
    forbidden_path_chars = set(r'*?"<>|')
    # Characters forbidden specifically in filenames (including separators and drive colons)
    forbidden_filename_chars = set(r'\/:*?"<>|')

    for full_path in file_names:
        # Normalize the input path (e.g., converts "C:\\Folder//File" to "C:\Folder\File")
        # EXPAND FIRST: Convert %TEMP% to real path before checking for forbidden chars
        expanded_path = os.path.expandvars(full_path)
        normalized_path = os.path.normpath(expanded_path)
        print(f"normalized path: {normalized_path}")

        directory = os.path.dirname(normalized_path)
        filename = os.path.basename(normalized_path)

        # 1. Clean the filename by removing all forbidden characters
        clean_filename = "".join(
            "" if ch in forbidden_filename_chars else ch for ch in filename
        )

        # 2. Clean the directory path
        path_chars = []
        for i, ch in enumerate(directory):
            # Special rule: Colon is ONLY allowed at index 1 (e.g., "C:")
            if ch == ":" and i != 1:
                continue
            if ch in forbidden_path_chars:
                continue
            path_chars.append(ch)

        clean_directory = "".join(path_chars)

        # 3. Combine cleaned parts and normalize again to ensure a clean final path
        suggested_fix = os.path.normpath(os.path.join(clean_directory, clean_filename))
        print(f"suggested_fix: {suggested_fix}")
        # If the cleaned version differs from the input, mark it as invalid
        if normalized_path != suggested_fix:
            invalid_files[full_path] = suggested_fix

    return invalid_files


def perform_file_renaming(old_file_names: list[str], new_file_names: list[str]):
    if len(old_file_names) != len(new_file_names):
        raise ValueError(f"Old_file_names[] has {len(old_file_names)} files but,"
                         f"new_file_names has {len(new_file_names)} files...?")

    for old_file_name, new_file_name in zip(old_file_names, new_file_names):
        try:
            # 1. Get folder path from new name
            final_new_name = os.path.expandvars(new_file_name)
            target_dir = os.path.dirname(final_new_name)

            # 2. If the folder does not exist, create it (including subfolders)
            if target_dir and not os.path.exists(target_dir):
                os.makedirs(target_dir)

            # 3. Use shutil.move instead of os.rename
            # shutil.move also works between different drives (C: -> D:)
            shutil.move(old_file_name, new_file_name)

        except (PermissionError, OSError) as e:
            print(f"Error {old_file_name}: {e}")
            raise OSError(
                f"Unable to process file {os.path.basename(old_file_name)}.\n\nError: {str(e)}"
            ) from e
