// Purpose: Flat, functional chat container displaying dialogue and coaching feedback.
import React, { useEffect, useRef, useState } from "react";
import MessageBubble from "./MessageBubble";

function ChatWindow({ 
  messages, 
  onSendMessage, 
  onEndSession, 
  isConnected, 
  coachingFeedback 
}) {
  const [inputText, setInputText] = useState("");
  const endOfMessagesRef = useRef(null);

  useEffect(() => {
    endOfMessagesRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = (e) => {
    e.preventDefault();
    if (!inputText.trim()) return;
    onSendMessage(inputText);
    setInputText("");
  };

  return (
    <div className="chat-window glass-card">
      <div className="chat-window-header">
        <div className="chat-status-indicator">
          <span className={`status-dot ${isConnected ? "connected" : "disconnected"}`} />
          <span>{isConnected ? "Connected to simulator" : "Connecting..."}</span>
        </div>
        <button 
          type="button" 
          className="btn-danger btn-sm" 
          onClick={onEndSession}
          disabled={messages.length === 0}
        >
          End & Grade Session
        </button>
      </div>

      <div className="chat-messages-container">
        {messages.length === 0 ? (
          <div className="chat-empty-view">
            <p>Type your opening sales pitch to begin training.</p>
          </div>
        ) : (
          messages.map((msg, i) => <MessageBubble key={i} message={msg} />)
        )}
        <div ref={endOfMessagesRef} />
      </div>

      {coachingFeedback && (
        <div className="coach-feedback-box">
          <strong className="coach-feedback-title">Coach Feedback:</strong>
          <p className="coach-feedback-text">{coachingFeedback}</p>
        </div>
      )}

      <form className="chat-input-form" onSubmit={handleSend}>
        <input
          type="text"
          className="form-input"
          placeholder={isConnected ? "Type a message..." : "WebSocket connecting..."}
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          disabled={!isConnected}
        />
        <button 
          type="submit" 
          className="btn-primary" 
          disabled={!isConnected || !inputText.trim()}
        >
          Send
        </button>
      </form>

      <style dangerouslySetInnerHTML={{ __html: `
        .chat-window {
          display: flex;
          flex-direction: column;
          height: 600px;
          padding: 0 !important;
          overflow: hidden;
          background-color: var(--bg-surface);
          border: 1px solid var(--border-solid);
        }
        .chat-window-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 12px 20px;
          border-bottom: 1px solid var(--border-solid);
          background-color: rgba(0, 0, 0, 0.15);
        }
        .chat-status-indicator {
          display: flex;
          align-items: center;
          gap: 8px;
          font-size: 0.85rem;
          color: var(--text-secondary);
        }
        .status-dot {
          width: 8px;
          height: 8px;
          border-radius: 50%;
          display: inline-block;
        }
        .status-dot.connected {
          background-color: var(--color-success);
        }
        .status-dot.disconnected {
          background-color: var(--color-warning);
        }
        .btn-sm {
          padding: 6px 12px;
          font-size: 0.8rem;
          border-radius: var(--radius-sm);
        }
        .chat-messages-container {
          flex: 1;
          padding: 20px;
          overflow-y: auto;
          background-color: rgba(0, 0, 0, 0.2);
          display: flex;
          flex-direction: column;
          gap: 12px;
        }
        .chat-empty-view {
          display: flex;
          justify-content: center;
          align-items: center;
          height: 100%;
          color: var(--text-muted);
          font-size: 0.95rem;
        }
        .coach-feedback-box {
          padding: 12px 20px;
          background-color: rgba(99, 102, 241, 0.1);
          border-top: 1px solid var(--border-solid);
          border-bottom: 1px solid var(--border-solid);
        }
        .coach-feedback-title {
          font-size: 0.8rem;
          color: var(--color-primary);
          text-transform: uppercase;
          letter-spacing: 0.05em;
          display: block;
          margin-bottom: 2px;
        }
        .coach-feedback-text {
          font-size: 0.9rem;
          color: var(--text-primary);
        }
        .chat-input-form {
          display: flex;
          gap: 12px;
          padding: 16px 20px;
          background-color: rgba(0, 0, 0, 0.15);
          border-top: 1px solid var(--border-solid);
        }
        .chat-input-form .form-input {
          flex: 1;
        }
        
        /* MessageBubble Layout Styles inside stream */
        .msg-row {
          display: flex;
          width: 100%;
          margin-bottom: 8px;
        }
        .msg-user-row {
          justify-content: flex-end;
        }
        .msg-customer-row {
          justify-content: flex-start;
        }
        .msg-system-row {
          justify-content: center;
          margin: 12px 0;
        }
        .msg-system-text {
          background-color: rgba(255, 255, 255, 0.05);
          border-radius: var(--radius-sm);
          padding: 4px 12px;
          font-size: 0.75rem;
          color: var(--text-muted);
        }
        .msg-container {
          max-width: 75%;
          display: flex;
          flex-direction: column;
          gap: 2px;
        }
        .msg-user-row .msg-container {
          align-items: flex-end;
        }
        .msg-meta {
          display: flex;
          gap: 6px;
          font-size: 0.7rem;
          color: var(--text-muted);
        }
        .msg-sender {
          font-weight: 600;
        }
        .msg-bubble {
          padding: 10px 14px;
          border-radius: var(--radius-md);
          font-size: 0.9rem;
          line-height: 1.4;
        }
        .msg-bubble-user {
          background-color: var(--color-primary);
          color: #FFFFFF;
          border-bottom-right-radius: 2px;
        }
        .msg-bubble-customer {
          background-color: #334155;
          color: var(--text-primary);
          border-bottom-left-radius: 2px;
          border: 1px solid var(--border-solid);
        }
        .msg-text {
          color: inherit;
        }
      ` }} />
    </div>
  );
}

export default ChatWindow;
