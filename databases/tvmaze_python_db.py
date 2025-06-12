from tvmaze.api import Api
from tvmaze.models import ResultSet, Model

from backend.media_record import MediaRecord
from databases.database import Database, retrieve_episode_name_from_episode_lookup


class TVMazePythonDB(Database):
    """
    Implementation of Database class to match MediaRecords to TVMaze, using the 'python-tvmaze' library.
    TVMaze source: https://www.tvmaze.com/.

    This DB does not support movies since TVMaze is a TV-only database.
    """

    def __init__(self, media_records: list[MediaRecord], is_tv_series: bool = False):
        super().__init__(media_records, is_tv_series)
        self.api = Api()

    def retrieve_media_titles_from_db(self) -> list[str | None]:
        """
        The TVMaze API will return the best match as the first element. This should be fine for most cases.

        However, for cases such as 'Doctor Who (2005)' and 'Doctor Who (2023)', this method will default to the newest
        listing. Users will get an opportunity to change the matched year from [auto] before matching with a database.
        """
        possible_listings: ResultSet[Model | None] = self.api.search.shows(self.media_records[0].title)

        if len(possible_listings) == 0:
            return [None] * len(self.media_records)

        # Default pick.
        selected_listing: Model = possible_listings[0]

        # If the user inputs a specific year or a year is matched from the filename, filter shows greater than
        # one year away from the input year, and pick the first element in the remaining list of possible shows.
        if self.media_records[0].year is not None:
            target_year: int = self.media_records[0].year

            # Get the first listing once listings are filtered within one year of the target year.
            # This should be 'good enough' to get the best matching show/listing for the user.
            selected_listing = filter_listings_within_one_year_of_target(possible_listings, target_year)[0]

        matched_show_id: int = selected_listing.id

        matched_episodes: ResultSet[Model | None] = self.api.show.episodes(matched_show_id)

        # Map: (Season, Episode number) to Episode name.
        episode_lookup = {(episode.season, episode.number): episode.name for episode in matched_episodes}

        result: list[str | None] = []

        for media_record in self.media_records:
            result.append(retrieve_episode_name_from_episode_lookup(media_record, episode_lookup))

        return result

    def retrieve_media_years_from_db(self) -> list[int | None]:
        """Return the premiere year of the series, padding them to the length of the input list of MediaRecords."""

        # If the media records list already contains the year, return it.
        if self.media_records[0].year is not None:
            return [self.media_records[0].year] * len(self.media_records)

        possible_listings: ResultSet[Model | None] = self.api.search.shows(self.media_records[0].title)

        if len(possible_listings) == 0:
            return [None] * len(self.media_records)

        # Since there's no matched year from the input list of MediaRecords, return the premiere year of the 1st result.
        return [get_premiere_year_of_listing(possible_listings[0])] * len(self.media_records)


def filter_listings_within_one_year_of_target(possible_listings: ResultSet[Model | None], target_year: int) -> list:
    """
    Filter a list of possible listings to within one year of the input target year.
    If filtering returns an empty list, return the input 'possible listings' list.
    """

    filtered = [listing for listing in possible_listings
                if (premiere_year := get_premiere_year_of_listing(listing)) is not None
                and abs(premiere_year - target_year) <= 1
                ] or possible_listings

    return filtered


def get_premiere_year_of_listing(listing: Model | None) -> int | None:
    """Returns the year of a listing/show's premiere, or None if it does not exist."""

    premiere_date = listing.premiered

    if premiere_date is not None:
        # Return only the year.
        return int(premiere_date[:4])

    return None
