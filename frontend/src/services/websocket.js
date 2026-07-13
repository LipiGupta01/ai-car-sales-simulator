// Purpose: WebSocket client connection utilities for real-time practice sessions.

export function createChatSocket(sessionId) {
  const wsBaseUrl = import.meta.env.VITE_WS_BASE_URL || "ws://localhost:8000/ws/chat";
  return new WebSocket(`${wsBaseUrl}/${sessionId}`);
}
