import { apiRequest } from './api.js';

async function checkApi() {
  const statusBox = document.getElementById('apiStatus');
  try {
    const data = await apiRequest('/health');
    statusBox.className = 'alert alert-success';
    statusBox.textContent = `API доступен: ${data.service}`;
  } catch (error) {
    statusBox.className = 'alert alert-danger';
    statusBox.textContent = `Нет связи с API: ${error.message}`;
  }
}

checkApi();
