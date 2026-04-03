import axios from "axios";

const api = axios.create({ baseURL: process.env.REACT_APP_API_URL || "http://localhost:8000" });

export const askQuestion = (formData) =>
  api.post("/api/v1/ask", formData, { headers: { "Content-Type": "multipart/form-data" } });
