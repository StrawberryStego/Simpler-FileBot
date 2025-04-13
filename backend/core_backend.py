from backend.media_record import MediaRecord


def match_titles_using_db_and_format(database) -> list[str]:
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
