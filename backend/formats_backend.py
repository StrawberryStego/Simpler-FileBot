from backend.json_config import JSONConfig

formats_json_config = JSONConfig(
    "formats.json",
    {
        "movie_format": "{movie_name} ({year})",
        "series_format": "{series_name} - S{season_number}E{episode_number} - {episode_title}"
    }
)


def retrieve_movies_format_from_formats_file():
    return formats_json_config.get("movie_format", "{movie_name} ({year})")


def save_new_movies_format_to_formats_file(new_movie_format: str):
    formats_json_config.set("movie_format", new_movie_format)


def retrieve_series_format_from_formats_file():
    return formats_json_config.get("series_format", "{series_name} - S{season_number}E{episode_number} - {episode_title}")


def save_new_series_format_to_formats_file(new_series_format: str):
    formats_json_config.set("series_format", new_series_format)
