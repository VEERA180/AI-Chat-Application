function InputArea({ input, setInput, sendMessage }) {
  return (
    <div className="input-area">
      <button className="attach-btn">📎</button>

      <input
        type="text"
        placeholder="Type your message..."
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter") {
            sendMessage();
          }
        }}
      />

      <button className="mic-btn">🎙️</button>

      <button
        className="send-btn"
        onClick={sendMessage}
      >
        ➤ Send
      </button>
    </div>
  );
}

export default InputArea;