import { useState } from "react";

export default function ChatInput({ onSend, loading }) {
  const [input, setInput] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;
    onSend(input);
    setInput("");
  };

  return (
    <form onSubmit={handleSubmit} className="flex gap-2 p-4 bg-white border-t">
      <input
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="Bạn cần hỗ trợ gì hôm nay?"
        className="flex-1 border border-gray-300 rounded-full px-4 py-2 text-sm outline-none focus:border-red-500"
        disabled={loading}
      />
      <button
        type="submit"
        disabled={loading || !input.trim()}
        className="bg-red-600 hover:bg-red-700 disabled:bg-gray-300 text-white rounded-full px-5 py-2 text-sm font-medium transition"
      >
        {loading ? "..." : "Gửi"}
      </button>
    </form>
  );
}