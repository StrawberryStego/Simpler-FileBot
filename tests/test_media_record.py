from backend.media_record import MediaRecord


def test_create_movie_record_successfully():
    media_record = MediaRecord("C:/Iron Man (2008).mkv")
    assert media_record.file_name == "Iron Man (2008).mkv"
    assert media_record.full_file_path == "C:/Iron Man (2008).mkv"
    assert media_record.title == "Iron Man"
    assert media_record.media_type == "movie"
    assert media_record.year == 2008


def test_create_episode_record_successfully():
    media_record = MediaRecord("X:/Hiya/TV Shows/The.Wire.S01E01.BluRay.1080p.DD.5.1.x264-MyGroup.mkv")
    assert media_record.file_name == "The.Wire.S01E01.BluRay.1080p.DD.5.1.x264-MyGroup.mkv"
    assert media_record.full_file_path == "X:/Hiya/TV Shows/The.Wire.S01E01.BluRay.1080p.DD.5.1.x264-MyGroup.mkv"
    assert media_record.title == "The Wire"
    assert media_record.media_type == "episode"
    assert media_record.year is None


def test_create_episode_without_series_name_in_file_name_successfully():
    media_record = MediaRecord("D:/Stuff/TV Shows/The West Wing/Season 2/S02E02 - Episode Name.mkv")
    assert media_record.title == "The West Wing"


def test_no_filename_sole_metadata_is_type():
    media_record = MediaRecord("")
    assert len(media_record.metadata) == 1


def test_media_record_str_function():
    media_record = MediaRecord("C:/My Folder/Hello There.mkv")
    assert str(media_record) == "Hello There.mkv"


def test_media_record_repr_function():
    media_record = MediaRecord("C:/AAA/MyFile.mkv")
    assert repr(media_record) == "C:/AAA/MyFile.mkv"


def test_list_has_movies():
    media_record_list = [MediaRecord("Interstellar (2014)"), MediaRecord("Iron Man (2008)")]
    assert MediaRecord.has_movies(media_record_list)


def test_list_has_no_movies():
    media_record_list = [MediaRecord("The.West.Wing.Ep01.mkv"), MediaRecord("The.Wire.Ep05.mkv")]
    assert not MediaRecord.has_movies(media_record_list)


def test_list_has_episodes():
    media_record_list = [MediaRecord("Fairy Tail S01E05.mp4"), MediaRecord("S05E11 - Pilot Program")]
    assert MediaRecord.has_episodes(media_record_list)


def test_list_has_no_episodes():
    media_record_list = [MediaRecord("Kung Fu Panda.mkv"), MediaRecord("Thunderbolts*(2025)"), MediaRecord("")]
    assert not MediaRecord.has_episodes(media_record_list)


def test_list_records_all_have_titles():
    media_record_list = [
        MediaRecord("Tropic Thunder.mkv"),
        MediaRecord("Star Wars - Episode 7.mkv"),
        MediaRecord("Boston Legal (Episode 9) - Title")]
    assert MediaRecord.all_have_titles(media_record_list)


def test_list_records_do_not_all_have_titles():
    media_record_list = [MediaRecord(""), MediaRecord(".mkv"), MediaRecord("()[].mkv")]
    assert not MediaRecord.all_have_titles(media_record_list)
