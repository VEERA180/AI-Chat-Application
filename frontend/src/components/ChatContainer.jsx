import { useState } from "react";
import Header from "./Header";
import MessageList from "./MessageList";
import InputArea from "./InputArea";

function ChatContainer() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");

  const sendMessage = () => {
    if (!input.trim()) return;

    setMessages([
      ...messages,
      {
        role: "user",
        text: input,
      },
    ]);

    setInput("");
  };

  return (
    <main className="chat-container">
      <Header />

      <MessageList messages={messages} />

      <InputArea
        input={input}
        setInput={setInput}
        sendMessage={sendMessage}
      />
    </main>
  );
}

export default ChatContainer;