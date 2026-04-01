import { useState, useCallback } from "react";
import { v4 as uuidv4 } from "uuid";
import { sendMessage, resetSession } from "../services/api";

const SESSION_ID = uuidv4(); // mỗi tab browser 1 session riêng

export function useChat() {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const sendQuery = useCallback(async (query) => {
    if (!query.trim()) return;

    // Thêm user message
    setMessages((prev) => [
      ...prev,
      { role: "user", content: query, id: uuidv4(), timestamp: Date.now() },
    ]);
    setLoading(true);
    setError(null);

    try {
      const data = await sendMessage(query, SESSION_ID);
      // Thêm bot message
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: data.answer,
          id: uuidv4(),
          timestamp: Date.now()
        },
      ]);
    } catch (err) {
      setError("Có lỗi xảy ra, vui lòng thử lại.");
    } finally {
      setLoading(false);
    }
  }, []);

  const clearChat = useCallback(async () => {
    await resetSession(SESSION_ID);
    setMessages([]);
  }, []);

  return { messages, loading, error, sendQuery, clearChat };
}

