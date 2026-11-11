import { apiRequest } from './api.js';
import { isLoggedIn } from './auth.js';
import {
  ALLOWED_FOR_LABELS, alertHtml, daysBetween, escapeHtml, formatMoney,
  photoUrl, renderNavbar, showAlert, todayIso,
} from './common.js';

renderNavbar();

const equipmentId = Number(new URLSearchParams(location.search).get('id'));

const messages = document.getElementById('messages');
const equipmentInfo = document.getElementById('equipmentInfo');
const breadcrumbName = document.getElementById('breadcrumbName');
const bookingCard = document.getElementById('bookingCard');
const bookingForm = document.getElementById('bookingForm');
const termsHint = document.getElementById('termsHint');
const startInput = document.getElementById('startDate');
const endInput = document.getElementById('endDate');
const commentInput = document.getElementById('userComment');
const availabilityBox = document.getElementById('availabilityBox');
const submitButton = document.getElementById('submitBooking');

let equipment = null;

function renderEquipment() {
  const terms = equipment.terms;
  document.title = `${equipment.name} — CampusGear`;
  breadcrumbName.textContent = equipment.name;

  const termsRows = terms
    ? `
      <dt class="col-sm-5">Максимальный срок</dt><dd class="col-sm-7">${terms.max_days} дн.</dd>
      <dt class="col-sm-5">Залог</dt><dd class="col-sm-7">${terms.deposit > 0 ? formatMoney(terms.deposit) : 'не требуется'}</dd>
      <dt class="col-sm-5">Штраф за просрочку</dt><dd class="col-sm-7">${formatMoney(terms.fine_per_day)} в день</dd>
      <dt class="col-sm-5">Кто может арендовать</dt><dd class="col-sm-7">${ALLOWED_FOR_LABELS[terms.allowed_for]}</dd>
      <dt class="col-sm-5">Требования</dt><dd class="col-sm-7">${escapeHtml(terms.requirements || '—')}</dd>`
    : '';

  equipmentInfo.innerHTML = `
    <img src="${photoUrl(equipment)}" class="equipment-photo mb-3" alt="${escapeHtml(equipment.name)}">
    <span class="badge text-bg-light border mb-2">${escapeHtml(equipment.category.name)}</span>
    <h1 class="h2">${escapeHtml(equipment.name)}</h1>
    <p class="text-muted">${escapeHtml(equipment.manufacturer || '')}</p>
    <p>${escapeHtml(equipment.description || '')}</p>
    <h2 class="h5 mt-4">Условия аренды</h2>
    <dl class="row">
      ${termsRows}
      <dt class="col-sm-5">Экземпляров в парке</dt><dd class="col-sm-7">${equipment.units_total} шт.</dd>
    </dl>`;

  if (terms) {
    termsHint.textContent = `Не более ${terms.max_days} дн. Залог: ${terms.deposit > 0 ? formatMoney(terms.deposit) : 'не требуется'}.`;
  }
}

async function loadEquipment() {
  if (!equipmentId) {
    equipmentInfo.innerHTML = '';
    showAlert(messages, 'Не указано, какое оборудование открыть. Вернитесь в каталог.');
    return;
  }
  try {
    equipment = await apiRequest(`/equipment/${equipmentId}`);
  } catch (error) {
    equipmentInfo.innerHTML = '';
    showAlert(messages, error.message);
    return;
  }
  renderEquipment();
  bookingCard.hidden = false;
}

/** Проверяет период на странице и спрашивает у сервера, есть ли свободные экземпляры. */
async function checkAvailability() {
  availabilityBox.innerHTML = '';
  const start = startInput.value;
  const end = endInput.value;
  if (!start || !end) {
    return false;
  }
  if (end < start) {
    availabilityBox.innerHTML = alertHtml('Дата окончания раньше даты начала', 'warning');
    return false;
  }
  const maxDays = equipment.terms ? equipment.terms.max_days : null;
  if (maxDays && daysBetween(start, end) > maxDays) {
    availabilityBox.innerHTML = alertHtml(`Максимальный срок аренды: ${maxDays} дн.`, 'warning');
    return false;
  }
  try {
    const data = await apiRequest(
      `/bookings/availability?equipment_id=${equipmentId}&start_date=${start}&end_date=${end}`
    );
    availabilityBox.innerHTML = data.available
      ? alertHtml(`Свободно: ${data.units_free} из ${data.units_total} шт.`, 'success')
      : alertHtml('На эти даты всё оборудование занято. Выберите другой период.', 'danger');
    return data.available;
  } catch (error) {
    availabilityBox.innerHTML = alertHtml(error.message, 'danger');
    return false;
  }
}

startInput.min = todayIso();
endInput.min = todayIso();
startInput.addEventListener('change', () => {
  if (!endInput.value || endInput.value < startInput.value) {
    endInput.value = startInput.value;
  }
  endInput.min = startInput.value;
  checkAvailability();
});
endInput.addEventListener('change', checkAvailability);

bookingForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  messages.innerHTML = '';

  if (!isLoggedIn()) {
    const next = encodeURIComponent(`equipment.html?id=${equipmentId}`);
    messages.innerHTML = `<div class="alert alert-warning" role="alert">
      Чтобы подать заявку, <a href="login.html?next=${next}">войдите</a> или
      <a href="register.html">зарегистрируйтесь</a>.</div>`;
    return;
  }
  if (!startInput.value || !endInput.value) {
    showAlert(messages, 'Выберите даты начала и окончания аренды', 'warning');
    return;
  }

  submitButton.disabled = true;
  try {
    await apiRequest('/bookings', {
      method: 'POST',
      body: JSON.stringify({
        equipment_id: equipmentId,
        start_date: startInput.value,
        end_date: endInput.value,
        user_comment: commentInput.value.trim() || null,
      }),
    });
    location.href = 'my-bookings.html?created=1';
  } catch (error) {
    showAlert(messages, error.message);
    submitButton.disabled = false;
    checkAvailability();
  }
});

loadEquipment();
