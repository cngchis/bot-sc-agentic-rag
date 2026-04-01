import { useEffect, useRef } from "react";
import Message from "./Message";

export default function ChatWindow({ messages, loading }) {
  const bottomRef = useRef(null);

  // Auto scroll xuống cuối
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  return (
    <div className="flex-1 overflow-y-auto p-4 bg-gray-100">
      {messages.length === 0 && (
        <div className="text-center text-gray-400 mt-20">
          <p className="text-4xl mb-3">🏦</p>
          <p className="font-medium">Xin chào! Tôi có thể giúp gì cho bạn?</p>
          <p className="text-sm mt-1">Hỏi về tài khoản, thẻ, vay vốn...</p>
        </div>
      )}

      {messages.map((msg) => (
        <Message key={msg.id} message={msg} />
      ))}

      {loading && (
        <div className="flex justify-start mb-3">
          <div className="w-8 h-8 rounded-full bg-red-600 flex items-center justify-center text-white text-sm mr-2 mt-1">
            🏦
          </div>
          <div className="bg-white shadow rounded-2xl rounded-tl-sm px-4 py-3">
            <div className="flex gap-1">
              <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: "0ms"}}/>
              <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: "150ms"}}/>
              <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: "300ms"}}/>
            </div>
          </div>
        </div>
      )}

      <div ref={bottomRef} />
    </div>
  );
}