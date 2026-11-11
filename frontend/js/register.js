import { apiRequest } from './api.js';
import { saveSession } from './auth.js';
import { renderNavbar, showAlert } from './common.js';

renderNavbar();

const messages = document.getElementById('messages');
const registerForm = document.getElementById('registerForm');
const submitButton = document.getElementById('submitRegister');

registerForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  if (!registerForm.reportValidity()) {
    return;
  }
  submitButton.disabled = true;

  const email = document.getElementById('email').value.trim();
  const password = document.getElementById('password').value;
  try {
    await apiRequest('/auth/register', {
      method: 'POST',
      body: JSON.stringify({
        full_name: document.getElementById('fullName').value.trim(),
        email,
        password,
        user_type: document.getElementById('userType').value,
        group_or_department: document.getElementById('groupOrDepartment').value.trim() || null,
        phone: document.getElementById('phone').value.trim() || null,
      }),
    });
    // После регистрации сразу входим в аккаунт
    const data = await apiRequest('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
    saveSession(data.access_token, data.user);
    location.href = 'index.html';
  } catch (error) {
    showAlert(messages, error.message);
    submitButton.disabled = false;
  }
});
