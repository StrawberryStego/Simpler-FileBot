import os

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
    Checks for invalid file names and returns a dictionary of
    {invalid_name: fix}.
    """
    forbidden_chars = set(r'\/:*?"<>|')
    invalid_files = {}

    for file_name in file_names:
        if any(ch in forbidden_chars for ch in file_name):
            # Replace forbidden characters with blanks.
            suggested_fix = ''.join('' if ch in forbidden_chars else ch for ch in file_name)
            invalid_files[file_name] = suggested_fix

    return invalid_files


def perform_file_renaming(old_file_names: list[str], new_file_names: list[str]):
    if len(old_file_names) != len(new_file_names):
        raise ValueError(f"Old_file_names[] has {len(old_file_names)} files but,"
                         f"new_file_names has {len(new_file_names)} files...?")

    for old_file_name, new_file_name in zip(old_file_names, new_file_names):
        # Other generic OSErrors are propagated to the caller.
        try:
            os.rename(old_file_name, new_file_name)
        except PermissionError:
            # Handle only the specific case where a file is being held by another process (Windows specific?).
            # Current handling is just ignoring the specific file and moving onto the next one.
            continue
