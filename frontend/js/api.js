import { API_URL } from './config.js';

/**
 * Универсальная обёртка над fetch.
 * Все запросы к API проходят через неё, поэтому их видно в консоли браузера.
 */
export async function apiRequest(path, options = {}) {
  const token = localStorage.getItem('token');
  const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) };
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(`${API_URL}${path}`, { ...options, headers });
  if (!response.ok) {
    throw new Error(`Ошибка запроса: ${response.status}`);
  }
  return response.json();
}
