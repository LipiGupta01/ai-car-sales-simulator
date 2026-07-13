// Purpose: Simple, clean bubble container to render chat messages.
import React from "react";

function MessageBubble({ message }) {
  const { role, content, timestamp } = message;
  const isUser = role === "user";
  const isSystem = role === "system";

  if (isSystem) {
    return (
      <div className="msg-row msg-system-row">
        <span className="msg-system-text">{content}</span>
      </div>
    );
  }

  const formatTime = (isoString) => {
    if (!isoString) return "";
    try {
      const date = new Date(isoString);
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } catch {
      return "";
    }
  };

  return (
    <div className={`msg-row ${isUser ? "msg-user-row" : "msg-customer-row"}`}>
      <div className="msg-container">
        <div className="msg-meta">
          <span className="msg-sender">{isUser ? "You" : "Customer"}</span>
          <span className="msg-time">{formatTime(timestamp)}</span>
        </div>
        <div className={`msg-bubble ${isUser ? "msg-bubble-user" : "msg-bubble-customer"}`}>
          <p className="msg-text">{content}</p>
        </div>
      </div>
    </div>
  );
}

export default MessageBubble;
