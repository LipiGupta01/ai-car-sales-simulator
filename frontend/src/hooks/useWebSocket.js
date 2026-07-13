// Purpose: Custom React hook to manage WebSocket connections, message history, and coaching feedback.
import { useEffect, useRef, useState } from "react";
import { createChatSocket } from "../services/websocket";

export function useWebSocket(sessionId) {
  const [isConnected, setIsConnected] = useState(false);
  const [messages, setMessages] = useState([]);
  const [coachingFeedback, setCoachingFeedback] = useState("");
  const socketRef = useRef(null);

  useEffect(() => {
    if (!sessionId) {
      setIsConnected(false);
      setMessages([]);
      setCoachingFeedback("");
      return;
    }

    const socket = createChatSocket(sessionId);
    socketRef.current = socket;

    socket.onopen = () => {
      setIsConnected(true);
    };

    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === "message") {
          setMessages((prev) => [...prev, {
            role: data.role,
            content: data.content,
            timestamp: data.timestamp
          }]);
        } else if (data.type === "coaching_feedback") {
          setCoachingFeedback(data.content);
        } else if (data.type === "system") {
          setMessages((prev) => [...prev, {
            role: "system",
            content: data.content,
            timestamp: data.timestamp
          }]);
        }
      } catch (err) {
        console.error("Error parsing websocket payload:", err);
      }
    };

    socket.onclose = () => {
      setIsConnected(false);
    };

    return () => {
      socket.close();
      socketRef.current = null;
      setIsConnected(false);
      setMessages([]);
      setCoachingFeedback("");
    };
  }, [sessionId]);

  const sendMessage = (content) => {
    if (socketRef.current && isConnected) {
      socketRef.current.send(JSON.stringify({ content }));
    }
  };

  return { isConnected, messages, coachingFeedback, sendMessage };
}
