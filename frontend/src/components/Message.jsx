import { useState } from "react";

export default function Message({ message }) {
  const isUser = message.role === "user";
  const [showTime, setShowTime] = useState(false);

  const formatTime = (timestamp) => {
    if (!timestamp) return "";
    return new Date(timestamp).toLocaleTimeString("vi-VN", {
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} mb-3`}>
      {!isUser && (
        <div className="w-8 h-8 rounded-full bg-red-600 flex items-center justify-center text-white text-sm mr-2 mt-1 shrink-0">
          🏦
        </div>
      )}
      <div className={`max-w-[75%]`}>
        <div
          className={`px-4 py-2 rounded-2xl text-sm leading-relaxed ${
            isUser
              ? "bg-red-600 text-white rounded-tr-sm"
              : "bg-white text-gray-800 shadow rounded-tl-sm"
          }`}
          onMouseEnter={() => setShowTime(true)}
          onMouseLeave={() => setShowTime(false)}
        >
          {message.content}
        </div>
        {/* Time tooltip */}
        <p className={`text-xs text-gray-400 mt-1 h-4 ${
          isUser ? "text-right" : "text-left ml-1"
        } ${showTime ? "visible" : "invisible"}`}>
          {formatTime(message.timestamp)}
        </p>
      </div>
    </div>
  );
}