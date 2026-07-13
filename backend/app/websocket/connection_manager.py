"""Purpose: WebSocket connection manager for active client sessions."""

import logging
from collections import defaultdict
from typing import DefaultDict
from fastapi import WebSocket

logger = logging.getLogger("websocket")


class ConnectionManager:
    """Tracks active websocket clients by session id."""

    def __init__(self) -> None:
        self.active_connections: DefaultDict[str, list[WebSocket]] = defaultdict(list)

    async def connect(self, session_id: str, websocket: WebSocket) -> None:
        """Accept and store a new websocket connection."""
        await websocket.accept()
        self.active_connections[session_id].append(websocket)
        logger.info(f"WebSocket client connected to session: {session_id}")

    def disconnect(self, session_id: str, websocket: WebSocket) -> None:
        """Remove websocket connection from active session list."""
        if session_id in self.active_connections:
            if websocket in self.active_connections[session_id]:
                self.active_connections[session_id].remove(websocket)
                logger.info(f"WebSocket client disconnected from session: {session_id}")
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]

    async def send_personal_message(self, message: str, websocket: WebSocket) -> None:
        """Send message directly to a specific socket."""
        await websocket.send_text(message)

    async def send_personal_json(self, data: dict, websocket: WebSocket) -> None:
        """Send JSON payload directly to a specific socket."""
        await websocket.send_json(data)

    async def broadcast(self, session_id: str, message: str) -> None:
        """Broadcast text message to all active sockets in a session."""
        connections = self.active_connections.get(session_id, [])
        for connection in connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Error broadcasting to socket in session {session_id}: {e}")

    async def broadcast_json(self, session_id: str, data: dict) -> None:
        """Broadcast JSON payload to all active sockets in a session."""
        connections = self.active_connections.get(session_id, [])
        for connection in connections:
            try:
                await connection.send_json(data)
            except Exception as e:
                logger.error(f"Error broadcasting JSON to socket in session {session_id}: {e}")
