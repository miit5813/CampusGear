import { apiRequest } from './api.js';
import { escapeHtml, formatMoney, photoUrl, renderNavbar, showAlert } from './common.js';

renderNavbar();

const filterForm = document.getElementById('filterForm');
const searchInput = document.getElementById('searchInput');
const categoryFilter = document.getElementById('categoryFilter');
const equipmentList = document.getElementById('equipmentList');
const messages = document.getElementById('messages');

function equipmentCard(item) {
  const terms = item.terms;
  const termsHtml = terms
    ? `<li>Срок аренды: до ${terms.max_days} дн.</li>
       <li>Залог: ${terms.deposit > 0 ? formatMoney(terms.deposit) : 'не требуется'}</li>`
    : '';
  return `
    <div class="col">
      <article class="card h-100 equipment-card shadow-sm">
        <img src="${photoUrl(item)}" class="card-img-top equipment-card__image" alt="${escapeHtml(item.name)}">
        <div class="card-body d-flex flex-column">
          <span class="badge text-bg-light border align-self-start mb-2">${escapeHtml(item.category.name)}</span>
          <h2 class="h5 card-title">${escapeHtml(item.name)}</h2>
          <p class="card-text text-muted small equipment-card__description">${escapeHtml(item.description || '')}</p>
          <ul class="list-unstyled small mb-3 mt-auto">
            ${termsHtml}
            <li>В парке: ${item.units_total} шт.</li>
          </ul>
          <a class="btn btn-primary" href="equipment.html?id=${item.id}">Подробнее</a>
        </div>
      </article>
    </div>`;
}

async function loadCategories() {
  try {
    const categories = await apiRequest('/categories');
    categoryFilter.insertAdjacentHTML(
      'beforeend',
      categories.map((c) => `<option value="${c.id}">${escapeHtml(c.name)}</option>`).join('')
    );
  } catch (error) {
    showAlert(messages, error.message);
  }
}

async function loadEquipment() {
  const params = new URLSearchParams();
  if (categoryFilter.value) {
    params.set('category_id', categoryFilter.value);
  }
  if (searchInput.value.trim()) {
    params.set('search', searchInput.value.trim());
  }

  equipmentList.innerHTML = `<div class="col-12 text-center py-5"><div class="spinner-border" role="status"><span class="visually-hidden">Загрузка...</span></div></div>`;
  try {
    const items = await apiRequest(`/equipment?${params.toString()}`);
    messages.innerHTML = '';
    equipmentList.innerHTML = items.length
      ? items.map(equipmentCard).join('')
      : `<div class="col-12"><p class="text-muted">Ничего не найдено. Попробуйте изменить поиск или категорию.</p></div>`;
  } catch (error) {
    equipmentList.innerHTML = '';
    showAlert(messages, error.message);
  }
}

filterForm.addEventListener('submit', (event) => {
  event.preventDefault();
  loadEquipment();
});
categoryFilter.addEventListener('change', loadEquipment);

loadCategories();
loadEquipment();
