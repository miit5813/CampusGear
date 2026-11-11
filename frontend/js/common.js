import { clearSession, getUser, isLoggedIn } from './auth.js';

export const STATUS_LABELS = {
  pending: ['На рассмотрении', 'warning'],
  approved: ['Одобрена', 'success'],
  rejected: ['Отклонена', 'danger'],
  cancelled: ['Отменена', 'secondary'],
  issued: ['Выдана', 'primary'],
  returned: ['Возвращена', 'info'],
  overdue: ['Просрочена', 'danger'],
};

export const ALLOWED_FOR_LABELS = {
  all: 'Все студенты и сотрудники',
  student: 'Только студенты',
  employee: 'Только сотрудники',
};

const CATEGORY_STYLES = {
  'Проекторы': ['📽️', '#cfe2ff'],
  'Камеры': ['📷', '#d1e7dd'],
  'Микрофоны': ['🎤', '#f8d7da'],
  'Штативы': ['🎞️', '#fff3cd'],
  'Лабораторные приборы': ['🔬', '#e2d9f3'],
  'Спортивный инвентарь': ['⚽', '#ffe5d0'],
};

/** Защита от внедрения HTML: все данные от пользователей выводим через эту функцию. */
export function escapeHtml(value) {
  return String(value ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

export function formatDate(iso) {
  const [year, month, day] = iso.slice(0, 10).split('-');
  return `${day}.${month}.${year}`;
}

export function formatMoney(value) {
  return `${Number(value).toLocaleString('ru-RU')} ₽`;
}

export function todayIso() {
  const now = new Date();
  const month = String(now.getMonth() + 1).padStart(2, '0');
  const day = String(now.getDate()).padStart(2, '0');
  return `${now.getFullYear()}-${month}-${day}`;
}

export function daysBetween(startIso, endIso) {
  return Math.round((Date.parse(endIso) - Date.parse(startIso)) / 86400000) + 1;
}

export function statusBadge(status) {
  const [label, color] = STATUS_LABELS[status] || [status, 'secondary'];
  return `<span class="badge text-bg-${color}">${label}</span>`;
}

export function alertHtml(message, type = 'danger') {
  return `<div class="alert alert-${type} alert-dismissible fade show" role="alert">
    ${escapeHtml(message)}
    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Закрыть"></button>
  </div>`;
}

export function showAlert(container, message, type = 'danger') {
  container.innerHTML = alertHtml(message, type);
}

/** Картинка-заглушка с иконкой категории, пока у оборудования нет настоящего фото. */
export function placeholderImage(categoryName) {
  const [emoji, background] = CATEGORY_STYLES[categoryName] || ['📦', '#e9ecef'];
  const svg =
    `<svg xmlns="http://www.w3.org/2000/svg" width="600" height="400">` +
    `<rect width="100%" height="100%" fill="${background}"/>` +
    `<text x="50%" y="50%" font-size="120" text-anchor="middle" dominant-baseline="central">${emoji}</text>` +
    `</svg>`;
  return `data:image/svg+xml;charset=utf-8,${encodeURIComponent(svg)}`;
}

export function photoUrl(item) {
  return item.main_photo_url || placeholderImage(item.category && item.category.name);
}

/** Рисует верхнее меню. Состав пунктов зависит от того, вошёл ли пользователь и какая у него роль. */
export function renderNavbar() {
  const header = document.getElementById('navbar');
  if (!header) {
    return;
  }
  const user = getUser();
  const currentPage = location.pathname.split('/').pop() || 'index.html';
  const link = (href, text) =>
    `<li class="nav-item"><a class="nav-link ${currentPage === href ? 'active' : ''}" href="${href}">${text}</a></li>`;

  let items = link('index.html', 'Каталог');
  let actions;
  if (isLoggedIn() && user) {
    items += link('my-bookings.html', 'Мои заявки');
    if (user.role === 'admin') {
      items += link('admin.html', 'Заявки (админ)');
    }
    actions = `
      <span class="navbar-text me-lg-3 mb-2 mb-lg-0">${escapeHtml(user.full_name)}</span>
      <button id="logoutButton" class="btn btn-outline-light btn-sm" type="button">Выйти</button>`;
  } else {
    actions = `
      <a class="btn btn-outline-light btn-sm me-2" href="login.html">Войти</a>
      <a class="btn btn-light btn-sm" href="register.html">Регистрация</a>`;
  }

  header.innerHTML = `
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
      <div class="container">
        <a class="navbar-brand fw-bold" href="index.html">CampusGear</a>
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse"
                data-bs-target="#mainNavbar" aria-controls="mainNavbar"
                aria-expanded="false" aria-label="Открыть меню">
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="mainNavbar">
          <ul class="navbar-nav me-auto">${items}</ul>
          <div class="d-flex flex-column flex-lg-row align-items-lg-center mt-2 mt-lg-0">${actions}</div>
        </div>
      </div>
    </nav>`;

  const logoutButton = document.getElementById('logoutButton');
  if (logoutButton) {
    logoutButton.addEventListener('click', () => {
      clearSession();
      location.href = 'index.html';
    });
  }
}
