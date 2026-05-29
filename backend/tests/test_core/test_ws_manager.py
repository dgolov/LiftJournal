from unittest.mock import AsyncMock, MagicMock

import pytest

from app.core.ws_manager import ConnectionManager


@pytest.fixture
def manager():
    return ConnectionManager()


@pytest.fixture
def mock_ws():
    ws = AsyncMock()
    ws.accept = AsyncMock()
    ws.send_json = AsyncMock()
    return ws


class TestConnect:
    async def test_accepts_websocket(self, manager, mock_ws):
        await manager.connect(user_id=1, websocket=mock_ws)

        mock_ws.accept.assert_called_once()

    async def test_stores_connection(self, manager, mock_ws):
        await manager.connect(user_id=1, websocket=mock_ws)

        assert manager._connections[1] is mock_ws

    async def test_replaces_existing_connection(self, manager, mock_ws):
        old_ws = AsyncMock()
        old_ws.accept = AsyncMock()
        await manager.connect(user_id=1, websocket=old_ws)
        await manager.connect(user_id=1, websocket=mock_ws)

        assert manager._connections[1] is mock_ws


class TestDisconnect:
    async def test_removes_connection(self, manager, mock_ws):
        await manager.connect(user_id=1, websocket=mock_ws)
        manager.disconnect(user_id=1)

        assert 1 not in manager._connections

    def test_noop_when_not_connected(self, manager):
        manager.disconnect(user_id=999)  # should not raise


class TestSend:
    async def test_sends_json_to_connected_user(self, manager, mock_ws):
        await manager.connect(user_id=1, websocket=mock_ws)
        payload = {"event": "notification", "data": {"id": "n-1"}}

        await manager.send(user_id=1, data=payload)

        mock_ws.send_json.assert_called_once_with(payload)

    async def test_noop_when_user_not_connected(self, manager):
        await manager.send(user_id=999, data={"event": "test"})
        # No exception raised

    async def test_disconnects_on_send_error(self, manager, mock_ws):
        await manager.connect(user_id=1, websocket=mock_ws)
        mock_ws.send_json.side_effect = Exception("connection closed")

        await manager.send(user_id=1, data={"event": "test"})

        assert 1 not in manager._connections

    async def test_multiple_users_independent(self, manager):
        ws1 = AsyncMock()
        ws1.accept = AsyncMock()
        ws2 = AsyncMock()
        ws2.accept = AsyncMock()

        await manager.connect(user_id=1, websocket=ws1)
        await manager.connect(user_id=2, websocket=ws2)

        await manager.send(user_id=1, data={"msg": "hello"})

        ws1.send_json.assert_called_once()
        ws2.send_json.assert_not_called()
