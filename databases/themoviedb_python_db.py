import tmdbsimple as tmdb

from backend.api_key_config import retrieve_the_movie_db_key
from backend.media_record import MediaRecord
from databases.database import Database


class TheMovieDBPythonDB(Database):
    """
    Implementation of Database class to match 'movie' & 'series' MediaRecords to TMDB, using the tmdbsimple library.
    TheMovieDB source: https://www.themoviedb.org/.

    This DB supports both movies and tv shows since TMDB supports both.
    """

    def __init__(self, media_records: list[MediaRecord], is_tv_series: bool = False):
        super().__init__(media_records, is_tv_series)

        retrieved_api_key = retrieve_the_movie_db_key()
        tmdb.API_KEY = retrieved_api_key
        # Timeout for connect & request after 5 seconds.
        tmdb.REQUESTS_TIMEOUT = 5

    def retrieve_media_titles_from_db(self) -> list[str | None]:
        matched_titles: list[str | None] = []

        if self.is_tv_series:
            # MediaRecord Episode Match.
            possible_listings: dict = tmdb.Search().tv(query=self.media_records[0].title).get("results", "")

            if len(possible_listings) == 0:
                return [None] * len(self.media_records)

            # Default pick.
            selected_listing = list(possible_listings)[0]

            if self.media_records[0].year is not None:
                target_year = self.media_records[0].year
                selected_listing = _find_best_listing_near_year(possible_listings, target_year, "first_air_date")

            for media_record in self.media_records:
                matched_titles.append(_retrieve_episode_title(selected_listing.get("id"), media_record))
        else:
            # MediaRecord Movie Match.
            for media_record in self.media_records:
                possible_listings: dict = tmdb.Search().movie(query=media_record.title).get("results", "")
                target_year: int | None = media_record.year

                if len(possible_listings) == 0:
                    matched_titles.append(None)
                    continue

                if target_year is None:
                    # Choose the first possible listing.
                    matched_titles.append(list(possible_listings)[0].get("title", None))
                else:
                    # Rare case where names might differentiate slightly and year is used to filter wrong names.
                    best_listing = _find_best_listing_near_year(possible_listings, target_year, "release_date")
                    matched_titles.append(best_listing.get("title", None))

        return matched_titles

    def retrieve_media_years_from_db(self) -> list[int | None]:
        # Return the 'series' release year.
        if self.is_tv_series:
            # Simply return the year if it already exists for a series.
            if self.media_records[0].year is not None:
                return [self.media_records[0].year] * len(self.media_records)

            possible_listings: dict = tmdb.Search().tv(query=self.media_records[0].title).get("results", "")
            if len(possible_listings) == 0:
                return [None] * len(self.media_records)

            # In this branch case, the user does not know the year of the series. Just select the first listing.
            listing_date = list(possible_listings)[0].get("first_air_date", None)

            return [int(listing_date[:4]) if listing_date is not None else None] * len(self.media_records)

        # Return the 'movie' release year of each MediaRecord.
        release_years: list[int | None] = []

        for media_record in self.media_records:
            # Just use the year attached to the MediaRecord if it exists.
            if media_record.year is not None:
                release_years.append(media_record.year)
                continue

            possible_listings: dict = tmdb.Search().movie(query=media_record.title).get("results", "")

            # In this branch case, the user does not know the year of the series. Just select the first listing.
            listing_date = list(possible_listings)[0].get("release_date", None)

            release_years.append(int(listing_date[:4]) if listing_date is not None else None)

        return release_years


def _find_best_listing_near_year(possible_listings: dict, target_year: int, identifier_for_year: str) -> dict:
    filtered: list = [listing for listing in possible_listings
                      if (release_year := _get_release_year_of_listing(listing, identifier_for_year)) is not None
                      and abs(release_year - target_year) <= 1
                      ] or possible_listings

    return filtered[0]


def _get_release_year_of_listing(listing: dict, identifier_for_year: str) -> int | None:
    premiere_date = listing.get(identifier_for_year, None)

    if premiere_date is not None:
        # Return only the year.
        return int(premiere_date[:4])

    return None


def _retrieve_episode_title(series_id: int, media_record: MediaRecord) -> str | None:
    """
    Return the episode title from TMDB database, given a MediaRecord.
    """
    # Default to season 1 if attribute is missing.
    media_record_season_number = media_record.metadata.get("season", 1)
    media_record_episode_values = media_record.metadata.get("episode", None)

    if media_record_episode_values is None:
        return None

    # media_record_episode_values could potentially be a list if there are multiple episodes. Pick the 1st one.
    media_record_episode_number = media_record_episode_values[0] \
        if isinstance(media_record_episode_values, list) else media_record_episode_values

    episode_info = tmdb.TV_Episodes(series_id, media_record_season_number, media_record_episode_number).info()

    return episode_info.get("name", None)
