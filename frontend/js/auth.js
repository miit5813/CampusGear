// Хранение токена и данных пользователя в браузере (localStorage)
const TOKEN_KEY = 'token';
const USER_KEY = 'user';

export function getToken() {
  try {
    return localStorage.getItem(TOKEN_KEY);
  } catch (error) {
    return null;
  }
}

export function getUser() {
  try {
    const raw = localStorage.getItem(USER_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch (error) {
    return null;
  }
}

export function saveSession(token, user) {
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem(USER_KEY, JSON.stringify(user));
}

export function clearSession() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}

export function isLoggedIn() {
  return Boolean(getToken());
}

/** Если пользователь не вошёл, отправляет на страницу входа. Возвращает true, если можно продолжать. */
export function requireLogin() {
  if (isLoggedIn()) {
    return true;
  }
  const page = location.pathname.split('/').pop() || 'index.html';
  location.href = `login.html?next=${encodeURIComponent(page + location.search)}`;
  return false;
}

/** Пропускает только администратора. */
export function requireAdmin() {
  if (!requireLogin()) {
    return false;
  }
  const user = getUser();
  if (!user || user.role !== 'admin') {
    location.href = 'index.html';
    return false;
  }
  return true;
}
