from tvmaze.api import Api
from tvmaze.models import Model, ResultSet

from backend.media_record import MediaRecord
from databases.tvmaze_python_db import get_premiere_year_of_listing, filter_listings_within_one_year_of_target, \
    TVMazePythonDB


def test_get_premiere_year_of_listing_successful():
    api = Api()

    listing: Model | None = api.search.single_show("The West Wing")

    assert get_premiere_year_of_listing(listing) == 1999


def test_filter_listings_within_one_year_of_target_successful():
    api = Api()
    target_year = 2005

    listings: ResultSet[Model | None] = api.search.shows("Doctor Who")

    assert len(listings) > 1

    for listing in filter_listings_within_one_year_of_target(listings, target_year):
        assert abs(get_premiere_year_of_listing(listing) - target_year) <= 1


def test_retrieve_media_years_from_db_successful():
    database = TVMazePythonDB([
        MediaRecord("The.West.Wing.S01E01.mkv"),
        MediaRecord("The.West.Wing.S07E01.mkv")],
        True)

    matched_media_years = database.retrieve_media_years_from_db()

    for year in matched_media_years:
        assert year == 1999


def test_retrieve_media_titles_from_db_successful():
    database = TVMazePythonDB([
        MediaRecord("The.West.Wing.S02E22.mkv"),
        MediaRecord("The.West.Wing.S04E23.mkv")],
        True)

    matched_media_titles = database.retrieve_media_titles_from_db()

    assert matched_media_titles[0] == "Two Cathedrals"
    assert matched_media_titles[1] == "Twenty Five"
