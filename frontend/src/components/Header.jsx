function Header() {
  return (
    <header className="chat-header">
      <div>
        <h1>RAG Chat Assistant</h1>
        <p>Ask questions about your documents</p>
      </div>

      <div className="header-actions">
        <span>📄</span>
        <span>☀️</span>
        <span className="profile">V</span>
        <span>⌄</span>
      </div>
    </header>
  );
}

export default Header;