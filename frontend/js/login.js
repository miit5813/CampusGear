import { apiRequest } from './api.js';
import { saveSession } from './auth.js';
import { renderNavbar, showAlert } from './common.js';

renderNavbar();

const params = new URLSearchParams(location.search);
const messages = document.getElementById('messages');
const loginForm = document.getElementById('loginForm');
const submitButton = document.getElementById('submitLogin');

if (params.get('expired')) {
  showAlert(messages, 'Сессия истекла. Войдите снова.', 'warning');
}

loginForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  submitButton.disabled = true;
  try {
    const data = await apiRequest('/auth/login', {
      method: 'POST',
      body: JSON.stringify({
        email: document.getElementById('email').value.trim(),
        password: document.getElementById('password').value,
      }),
    });
    saveSession(data.access_token, data.user);
    // Возвращаем туда, откуда пришли, но только на страницы этого сайта
    const next = params.get('next');
    location.href = next && /^[\w-]+\.html/.test(next) ? next : 'index.html';
  } catch (error) {
    showAlert(messages, error.message);
    submitButton.disabled = false;
  }
});
