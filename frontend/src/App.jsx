import Header from "./components/Header";
import ChatWindow from "./components/ChatWindow";
import ChatInput from "./components/ChatInput";
import { useChat } from "./hooks/useChat";

export default function App() {
  const { messages, loading, error, sendQuery, clearChat } = useChat();

  return (
    <div className="flex flex-col h-screen max-w-2xl mx-auto shadow-xl">
      <Header onClear={clearChat} />
      <ChatWindow messages={messages} loading={loading} />
      {error && (
        <p className="text-center text-red-500 text-sm py-2">{error}</p>
      )}
      <ChatInput onSend={sendQuery} loading={loading} />
    </div>
  );
}