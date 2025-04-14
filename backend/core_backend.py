import os

from backend.media_record import MediaRecord
from databases.database import Database


def match_titles_using_db_and_format(database: Database) -> list[str]:
    formatted_matched_titles = []
    media_records: list[MediaRecord] = database.media_records

    matched_titles = database.retrieve_media_titles_from_db()
    matched_years = database.retrieve_media_years_from_db()

    for i, item in enumerate(media_records):
        media_record = item
        media_title = matched_titles[i]
        media_year = matched_years[i]

        if database.is_tv_series:
            season_number = media_record.metadata.get("season")
            episode_number = media_record.metadata.get("episode")

            formatted_matched_titles.append(f"S{season_number:02d}E{episode_number:02d} - "
                                            f"{media_title}.{media_record.metadata.get('container')}")
        else:
            formatted_matched_titles.append(f"{media_title} ({media_year}).{media_record.metadata.get('container')}")

    return formatted_matched_titles


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
    for i, old_file_name in enumerate(old_file_names):
        new_file_name = new_file_names[i]

        try:
            os.rename(old_file_name, new_file_name)
        except OSError as e:
            print(f"Error renaming {old_file_name} to {new_file_name}: {e}")
