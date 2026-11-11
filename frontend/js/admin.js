import { apiRequest } from './api.js';
import { requireAdmin } from './auth.js';
import { escapeHtml, formatDate, renderNavbar, showAlert, statusBadge } from './common.js';

function bookingCard(booking) {
  const isPending = booking.status === 'pending';
  return `
    <div class="col">
      <article class="card h-100 shadow-sm">
        <div class="card-body">
          <div class="d-flex justify-content-between align-items-start mb-2">
            <h3 class="h6 mb-0">Заявка №${booking.id}</h3>
            ${statusBadge(booking.status)}
          </div>
          <p class="mb-1"><strong>Оборудование:</strong> ${escapeHtml(booking.equipment.name)}</p>
          <p class="mb-1"><strong>Пользователь:</strong> ${escapeHtml(booking.user.full_name)} (${escapeHtml(booking.user.email)})</p>
          <p class="mb-1"><strong>Период:</strong> ${formatDate(booking.start_date)} — ${formatDate(booking.end_date)}</p>
          ${booking.user_comment ? `<p class="mb-1"><strong>Комментарий пользователя:</strong> ${escapeHtml(booking.user_comment)}</p>` : ''}
          ${booking.unit ? `<p class="mb-1"><strong>Назначен экземпляр:</strong> ${escapeHtml(booking.unit.inventory_number)}</p>` : ''}
          ${booking.admin_comment ? `<p class="mb-1"><strong>Комментарий администратора:</strong> ${escapeHtml(booking.admin_comment)}</p>` : ''}
          ${isPending ? `
            <label class="form-label small mt-2" for="comment-${booking.id}">Комментарий для пользователя (необязательно)</label>
            <textarea id="comment-${booking.id}" class="form-control form-control-sm" rows="2" maxlength="500"></textarea>` : ''}
        </div>
        ${isPending ? `
          <div class="card-footer bg-transparent d-flex gap-2">
            <button class="btn btn-success btn-sm" type="button" data-action="approve" data-id="${booking.id}">Одобрить</button>
            <button class="btn btn-outline-danger btn-sm" type="button" data-action="reject" data-id="${booking.id}">Отклонить</button>
          </div>` : ''}
      </article>
    </div>`;
}

function init() {
  renderNavbar();

  const messages = document.getElementById('messages');
  const statusFilter = document.getElementById('statusFilter');
  const bookingList = document.getElementById('bookingList');

  async function loadBookings() {
    const query = statusFilter.value ? `?status=${statusFilter.value}` : '';
    try {
      const bookings = await apiRequest(`/bookings${query}`);
      bookingList.innerHTML = bookings.length
        ? bookings.map(bookingCard).join('')
        : '<div class="col-12"><p class="text-muted">Заявок с таким статусом нет.</p></div>';
    } catch (error) {
      showAlert(messages, error.message);
    }
  }

  statusFilter.addEventListener('change', loadBookings);

  bookingList.addEventListener('click', async (event) => {
    const button = event.target.closest('button[data-action]');
    if (!button) {
      return;
    }
    const { action, id } = button.dataset;
    const commentField = document.getElementById(`comment-${id}`);
    button.disabled = true;
    try {
      await apiRequest(`/bookings/${id}/${action}`, {
        method: 'POST',
        body: JSON.stringify({ admin_comment: commentField && commentField.value.trim() ? commentField.value.trim() : null }),
      });
      showAlert(messages, action === 'approve' ? `Заявка №${id} одобрена` : `Заявка №${id} отклонена`, 'success');
    } catch (error) {
      showAlert(messages, error.message);
    }
    loadBookings();
  });

  loadBookings();
}

if (requireAdmin()) {
  init();
}
