from src import preferences
import time
from unittest.mock import patch, ANY, MagicMock

@patch("preferences.Preferences")
def test_PreferencesFileHandler_onModified(mock_pref):
    obj = preferences.PreferencesFileHandler(mock_pref)
    time.sleep(1)
    obj.on_modified(None)
    mock_pref.loadPreferencesFromFile.assert_called()

@patch("preferences.Preferences")
def test_PreferencesFileHandler_on_created(mock_pref):
    obj = preferences.PreferencesFileHandler(mock_pref)
    obj.on_created(None)
    mock_pref.loadPreferencesFromFile.assert_called()

@patch("preferences.Preferences")
def test_PreferencesFileHandler_on_deleted(mock_pref):
    obj = preferences.PreferencesFileHandler(mock_pref)
    obj.on_deleted(None)
    mock_pref.clear.assert_called()