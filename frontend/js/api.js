import { API_URL } from './config.js';
import { clearSession, getToken } from './auth.js';

export class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.status = status;
  }
}

/**
 * Универсальная обёртка над fetch. Все запросы к backend идут через неё,
 * поэтому в консоли браузера видно каждый запрос и ответ.
 */
export async function apiRequest(path, options = {}) {
  const method = options.method || 'GET';
  const token = getToken();
  const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) };
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  console.log(`API → ${method} ${path}`);

  let response;
  try {
    response = await fetch(`${API_URL}${path}`, { ...options, headers });
  } catch (error) {
    console.error(`API ✗ ${method} ${path}`, error);
    throw new ApiError('Не удалось связаться с сервером. Проверьте, что backend запущен.', 0);
  }

  let data = null;
  try {
    data = await response.json();
  } catch (error) {
    data = null;
  }
  console.log(`API ← ${response.status} ${method} ${path}`, data);

  if (!response.ok) {
    // Токен устарел: сбрасываем вход и отправляем на страницу входа
    if (response.status === 401 && token && !path.startsWith('/auth/login')) {
      clearSession();
      location.href = 'login.html?expired=1';
    }
    let message = 'Ошибка запроса';
    if (data && typeof data.detail === 'string') {
      message = data.detail;
    } else if (response.status === 422) {
      message = 'Проверьте правильность введённых данных';
    }
    throw new ApiError(message, response.status);
  }
  return data;
}
