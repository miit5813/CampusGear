import { apiRequest } from './api.js';
import { getUser, requireLogin } from './auth.js';
import { escapeHtml, formatDate, renderNavbar, showAlert, statusBadge } from './common.js';

const ACTIVE_STATUSES = ['pending', 'approved', 'issued', 'overdue'];
const CANCELLABLE_STATUSES = ['pending', 'approved'];

const USER_TYPE_LABELS = { student: 'Студент', employee: 'Сотрудник' };

function returnInfo(booking) {
  switch (booking.status) {
    case 'pending':
      return 'Ожидает решения администратора';
    case 'approved':
      return `Одобрено. Выдача с ${formatDate(booking.start_date)}`;
    case 'issued':
      return `Выдано. Вернуть до ${formatDate(booking.end_date)}`;
    case 'overdue':
      return 'Срок истёк. Верните оборудование как можно скорее';
    case 'returned':
      return 'Оборудование возвращено';
    case 'rejected':
      return 'Заявка отклонена';
    case 'cancelled':
      return 'Заявка отменена';
    default:
      return '';
  }
}

function bookingCard(booking) {
  const canCancel = CANCELLABLE_STATUSES.includes(booking.status);
  return `
    <div class="col">
      <article class="card h-100 shadow-sm">
        <div class="card-body">
          <div class="d-flex justify-content-between align-items-start mb-2">
            <h3 class="h6 mb-0"><a href="equipment.html?id=${booking.equipment.id}">${escapeHtml(booking.equipment.name)}</a></h3>
            ${statusBadge(booking.status)}
          </div>
          <p class="mb-1"><strong>Период:</strong> ${formatDate(booking.start_date)} — ${formatDate(booking.end_date)}</p>
          ${booking.unit ? `<p class="mb-1"><strong>Инвентарный номер:</strong> ${escapeHtml(booking.unit.inventory_number)}</p>` : ''}
          <p class="mb-1"><strong>Статус возврата:</strong> ${returnInfo(booking)}</p>
          ${booking.admin_comment ? `<p class="mb-0 small"><strong>Комментарий администратора:</strong> ${escapeHtml(booking.admin_comment)}</p>` : ''}
        </div>
        ${canCancel ? `<div class="card-footer bg-transparent">
          <button class="btn btn-outline-danger btn-sm" type="button" data-cancel-id="${booking.id}">Отменить заявку</button>
        </div>` : ''}
      </article>
    </div>`;
}

function init() {
  renderNavbar();

  const messages = document.getElementById('messages');
  const activeList = document.getElementById('activeList');
  const historyList = document.getElementById('historyList');
  const user = getUser();

  document.getElementById('profileName').textContent = user.full_name;
  document.getElementById('profileDetails').textContent =
    `${user.email} · ${USER_TYPE_LABELS[user.user_type] || ''}${user.group_or_department ? ' · ' + user.group_or_department : ''}`;

  if (new URLSearchParams(location.search).get('created')) {
    showAlert(messages, 'Заявка отправлена. Ожидайте решения администратора, статус появится здесь.', 'success');
  }

  async function loadBookings() {
    try {
      const bookings = await apiRequest('/bookings/my');
      const active = bookings.filter((b) => ACTIVE_STATUSES.includes(b.status));
      const history = bookings.filter((b) => !ACTIVE_STATUSES.includes(b.status));
      activeList.innerHTML = active.length
        ? active.map(bookingCard).join('')
        : '<div class="col-12"><p class="text-muted">Активных аренд нет. <a href="index.html">Выбрать оборудование</a></p></div>';
      historyList.innerHTML = history.length
        ? history.map(bookingCard).join('')
        : '<div class="col-12"><p class="text-muted">История пока пуста.</p></div>';
    } catch (error) {
      showAlert(messages, error.message);
    }
  }

  document.body.addEventListener('click', async (event) => {
    const button = event.target.closest('button[data-cancel-id]');
    if (!button || !confirm('Отменить заявку?')) {
      return;
    }
    button.disabled = true;
    try {
      await apiRequest(`/bookings/${button.dataset.cancelId}/cancel`, { method: 'POST' });
      showAlert(messages, 'Заявка отменена', 'success');
    } catch (error) {
      showAlert(messages, error.message);
    }
    loadBookings();
  });

  loadBookings();
}

if (requireLogin()) {
  init();
}
