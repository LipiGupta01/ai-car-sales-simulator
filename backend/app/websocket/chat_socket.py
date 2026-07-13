"""Purpose: WebSocket route for real-time chat transport and simulator dialogue routing."""

import json
from datetime import datetime, timezone
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import logging

from app.core.database import SessionLocal
from app.services.conversation_orchestrator import ConversationOrchestrator
from app.models.session import Session as DbSession
from app.models.message import Message

logger = logging.getLogger("websocket")
router = APIRouter()


class SimpleConnectionManager:
    """Tracks simple active websocket connections for testing."""

    def __init__(self) -> None:
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info("WebSocket connected.")

    def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info("WebSocket disconnected.")


manager = SimpleConnectionManager()


@router.websocket("/ws/chat/{session_id}")
async def chat_socket(websocket: WebSocket, session_id: str) -> None:
    """Handle websocket connection, transmit past chat history, and execute simulation turns."""
    await manager.connect(websocket)
    # 1. Scope database session to initial connection data loading
    db = SessionLocal()
    try:
        db_session = db.query(DbSession).filter(DbSession.external_id == session_id).first()
        if db_session:
            past_msgs = (
                db.query(Message)
                .filter(Message.session_id == db_session.id)
                .order_by(Message.created_at.asc())
                .all()
            )
            for msg in past_msgs:
                await websocket.send_json({
                    "type": "message",
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.created_at.isoformat()
                })
        else:
            await websocket.send_json({
                "type": "system",
                "content": f"Connected to practice room. Session: {session_id}",
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
    except Exception as e:
        logger.error(f"Error loading initial connection chat history: {e}")
    finally:
        db.close()

    try:
        while True:
            data_str = await websocket.receive_text()
            try:
                data = json.loads(data_str)
                user_content = data.get("content", "").strip()
            except json.JSONDecodeError:
                user_content = data_str.strip()

            if not user_content:
                continue

            # 2. Scope database session per individual chat message turn
            db = SessionLocal()
            try:
                orchestrator = ConversationOrchestrator(db)
                turn_result = await orchestrator.process_message(session_id, user_content)
            except Exception as e:
                logger.error(f"Error processing websocket message turn: {e}")
                turn_result = None
            finally:
                db.close()

            if turn_result:
                # 1. Return the customer response
                await websocket.send_json({
                    "type": "message",
                    "role": "assistant",
                    "content": turn_result["customer_reply"],
                    "timestamp": turn_result["customer_msg_timestamp"]
                })

                # 2. Return coaching feedback
                await websocket.send_json({
                    "type": "coaching_feedback",
                    "content": turn_result["coaching_feedback"],
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })

    except WebSocketDisconnect:
        manager.disconnect(websocket)
