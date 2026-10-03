function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="logo-section">
        <div className="logo">🤖</div>
        <h2>RAG Chat<br />Assistant</h2>
      </div>

      <button className="new-chat-btn">
        + New Chat
      </button>

      <div className="sidebar-section">
        <h3>Recent Conversations</h3>
      </div>

      <div className="sidebar-bottom">
        <div>⚙️ Settings</div>
        <div>❓ Help</div>
      </div>
    </aside>
  );
}

export default Sidebar;