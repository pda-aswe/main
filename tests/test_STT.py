from src import STT
from unittest.mock import patch, ANY, MagicMock

def test_recordCallback():
    obj = STT.STT()

    with patch.object(obj, 'audioQueue') as mock_queue:
        obj.recordCallback(int("deadbeef",16),None,None,None)
        mock_queue.put.assert_called_with(bytes(int("deadbeef",16)))