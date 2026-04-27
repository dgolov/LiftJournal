from fastapi import WebSocket


class ConnectionManager:
    def __init__(self) -> None:
        self._connections: dict[int, WebSocket] = {}

    async def connect(self, user_id: int, websocket: WebSocket) -> None:
        await websocket.accept()
        self._connections[user_id] = websocket

    def disconnect(self, user_id: int) -> None:
        self._connections.pop(user_id, None)

    async def send(self, user_id: int, data: dict) -> None:
        ws = self._connections.get(user_id)
        if ws is None:
            return
        try:
            await ws.send_json(data)
        except Exception:
            self.disconnect(user_id)


manager = ConnectionManager()
