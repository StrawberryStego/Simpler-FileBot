from backend.settings_backend import retrieve_settings_as_dictionary, get_theme_from_settings


def test_retrieve_settings_as_dictionary():
    settings = retrieve_settings_as_dictionary()
    assert isinstance(settings, dict)


def test_theme_from_settings_is_light_or_dark():
    assert get_theme_from_settings() in ("Light", "Dark")
