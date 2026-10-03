function MessageList({ messages }) {
  return (
    <section className="messages">
      {messages.length === 0 ? (
        <div className="welcome-card">
          <div className="welcome-icon">🤖</div>

          <div>
            <h2>Welcome to RAG Chat Assistant! 👋</h2>

            <p>
              I can help you answer questions about your documents.
            </p>

            <h3>Try asking:</h3>

            <div className="suggestions">
              <button>Summarize this document</button>
              <button>Find key information</button>
              <button>Compare data</button>
            </div>
          </div>
        </div>
      ) : (
        messages.map((message, index) => (
          <div
            key={index}
            className={`message ${
              message.role === "user"
                ? "user-message"
                : "bot-message"
            }`}
          >
            {message.text}
          </div>
        ))
      )}
    </section>
  );
}

export default MessageList;