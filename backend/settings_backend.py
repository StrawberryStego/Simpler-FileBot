from PySide6.QtGui import QGuiApplication, Qt

from backend.json_config import JSONConfig

# Lazy created since Qt.ColorScheme does not work until after app is fully built.
_settings_json_config: JSONConfig | None = None


# pylint: disable=global-statement
def ensure() -> JSONConfig:
    """Ensure settings_json_config is built."""
    global _settings_json_config

    if _settings_json_config is None:
        _settings_json_config = JSONConfig(
            "settings.json",
            {
                "theme": (Qt.ColorScheme.Dark.name
                          if QGuiApplication.styleHints().colorScheme() == Qt.ColorScheme.Unknown
                          else QGuiApplication.styleHints().colorScheme().name),
                "excluded_folders": [],
                "use_only_filename_for_analysis": False
            }
        )

    return _settings_json_config


def retrieve_theme_from_settings() -> str:
    """Returns the theme from settings.json. Defaults to 'Dark' if settings are erroneous."""
    return ensure().get("theme", "Dark")


def save_new_theme_to_settings(scheme: Qt.ColorScheme):
    """Update the “theme” key in settings.json to either 'Light' or 'Dark'."""
    ensure().set("theme", scheme.name)


def add_excluded_folder(folder_path: str):
    """Add a folder to the 'excluded_folders' list in settings.json."""
    ensure().add("excluded_folders", folder_path)


def remove_excluded_folder(folder_path: str):
    """Remove a folder from the 'excluded_folders' list in settings.json."""
    ensure().remove("excluded_folders", folder_path)


def retrieve_excluded_folders() -> list[str]:
    return ensure().get("excluded_folders", [])


def retrieve_filename_analysis_only_flag() -> bool:
    return ensure().get("use_only_filename_for_analysis", False)


def set_filename_analysis_only_flag(new_value: bool):
    return ensure().set("use_only_filename_for_analysis", new_value)


def delete_and_recreate_settings_file():
    ensure().delete_and_recreate_file()


def get_settings_file_path():
    return ensure().path
