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

@patch("watchdog.observers.polling.PollingObserver")
@patch("preferences.PreferencesFileHandler")
@patch("messenger.Messenger")
def test_Preferences_loadPreferencesFromFile(mock_messenger, mock_pref, mock_observer):
    with patch('json.loads') as mock_json, patch("builtins.open"):
        obj = preferences.Preferences("/etc/os-release")
        mock_json.assert_called()

@patch("watchdog.observers.polling.PollingObserver")
@patch("preferences.PreferencesFileHandler")
@patch("messenger.Messenger")
@patch("builtins.open")
@patch('json.loads')
def test_Preferences_clear(mock_json, mock_open, mock_messenger, mock_pref, mock_observer):
    obj = preferences.Preferences("/etc/os-release")
    
    try:
        obj.clear()
        assert True
    except:
        assert False

@patch("watchdog.observers.polling.PollingObserver")
@patch("preferences.PreferencesFileHandler")
@patch("messenger.Messenger")
@patch("builtins.open")
@patch('json.loads')
def test_Preferences_stop(mock_json, mock_open, mock_messenger, mock_pref, mock_observer):
    obj = preferences.Preferences("/etc/os-release")
    
    with patch.object(obj,'observer') as mock_observer_object:
        obj.stop()
        mock_observer_object.stop.assert_called()

@patch("watchdog.observers.polling.PollingObserver")
@patch("preferences.PreferencesFileHandler")
@patch("messenger.Messenger")
@patch("builtins.open")
@patch('json.loads')
def test_Preferences_jsonDifference(mock_json, mock_open, mock_messenger, mock_pref, mock_observer):
    obj = preferences.Preferences("/etc/os-release")
    
    struct1 = {"test1":"test2","asdf":2}
    struct2 = {"test1":"test2","asdf":1}

    assert obj._Preferences__jsonDifference(struct1,struct2) == {"asdf":1}

@patch("watchdog.observers.polling.PollingObserver")
@patch("preferences.PreferencesFileHandler")
@patch("messenger.Messenger")
@patch("builtins.open")
@patch('json.loads')
def test_Preferences_sendPreference(mock_json, mock_open, mock_messenger, mock_pref, mock_observer):
    obj = preferences.Preferences("/etc/os-release")

    with patch.object(obj,'mqttClient') as mock_mqtt:
        obj._Preferences__sendPreference("path","value")
        mock_mqtt.publish.assert_called_with("path","value")

@patch("watchdog.observers.polling.PollingObserver")
@patch("preferences.PreferencesFileHandler")
@patch("messenger.Messenger")
@patch("builtins.open")
@patch('json.loads')
def test_Preferences_sendPreferenceStructure(mock_json, mock_open, mock_messenger, mock_pref, mock_observer):
    obj = preferences.Preferences("/etc/os-release")

    with patch.object(obj,'_Preferences__sendPreference') as mock_send:
        obj._Preferences__sendPreferenceStructure("path","value")
        mock_send.assert_called_with("path","value")