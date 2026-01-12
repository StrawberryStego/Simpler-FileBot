import sys
import os

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    # If sys._MEIPASS does not exist, the current directory is used
    base_path = getattr(sys, '_MEIPASS', os.path.abspath(".")) # pylint: disable=no-member,protected-access

    return os.path.join(base_path, relative_path)
