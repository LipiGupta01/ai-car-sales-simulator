// Purpose: API client instance for backend REST communication.
import axios from "axios";

let baseURL = import.meta.env.VITE_API_URL || import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";

if (baseURL && !baseURL.endsWith("/api/v1") && !baseURL.endsWith("/api/v1/")) {
  if (baseURL.endsWith("/")) {
    baseURL = baseURL.slice(0, -1);
  }
  baseURL = `${baseURL}/api/v1`;
}

const api = axios.create({
  baseURL,
  timeout: 45000
});

export default api;
