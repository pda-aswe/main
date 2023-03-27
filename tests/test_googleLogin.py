from src import googleLogin
from unittest.mock import patch, ANY, MagicMock

@patch("os.path.exists")
@patch("google.oauth2.credentials.Credentials.from_authorized_user_file")
def test_connect(mock_credentials,mock_exists):
    googleLogin.connect()
    mock_credentials.assert_called_with('credentials/token.json',['https://www.googleapis.com/auth/gmail.send','https://www.googleapis.com/auth/calendar'])