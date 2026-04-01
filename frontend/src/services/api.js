import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export const sendMessage = async (query, sessionId) => {
  const response = await axios.post(`${API_URL}/api/v1/chat`, {
    query,
    session_id: sessionId,
    stream: false,
  });
  return response.data;
};

export const resetSession = async (sessionId) => {
  await axios.delete(`${API_URL}/api/v1/chat/${sessionId}`);
};