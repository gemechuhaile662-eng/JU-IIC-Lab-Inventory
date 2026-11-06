// =========================================================
// manual.js — Search and pick item manually
// =========================================================

const input = document.getElementById('search');
const list = document.getElementById('itemList');

let allItems = [];
let correctionLogId = null;

// Check if this is a correction flow
const urlParams = new URLSearchParams(location.search);
if (urlParams.get('correct_log')) {
  correctionLogId = urlParams.get('correct_log');
}

// ---------- Load items on page load ----------
(async () => {
  try {
    allItems = await api.get('/api/items');
    render(allItems);
  } catch (err) {
    list.innerHTML = '<li class="empty">Could not load items: ' + err.message + '</li>';
  }
})();

// ---------- Search filter ----------
input.addEventListener('input', () => {
  const q = input.value.trim().toLowerCase();

  if (!q) {
    render(allItems);
    return;
  }

  const filtered = allItems.filter((i) =>
    (i.name || '').toLowerCase().includes(q) ||
    (i.asset_tag || '').toLowerCase().includes(q) ||
    (i.qr_code || '').toLowerCase().includes(q)
  );

  render(filtered);
});

// ---------- Render item list ----------
function render(items) {
  if (!items.length) {
    list.innerHTML = '<li class="empty">No items match your search.</li>';
    return;
  }

  list.innerHTML = items.map((i, idx) => `
    <li class="item-row" onclick="pickItem(${idx})">
      <div>
        <strong>${i.name}</strong>
        <small>
          ${i.item_type === 'equipment' ? 'Equipment' : 'Component'}
          ${i.asset_tag ? ' · ' + i.asset_tag : ''}
          ${i.qr_code ? ' · ' + i.qr_code : ''}
        </small>
      </div>
      <span>›</span>
    </li>
  `).join('');

  // Store current filtered list for pickItem
  window._currentItems = items;
}

// ---------- Pick an item ----------
async function pickItem(idx) {
  const item = window._currentItems[idx];
  if (!item) return;

  // If this was a correction flow, log the correction
  if (correctionLogId) {
    try {
      await api.post('/api/recognition/correct', {
        log_id: correctionLogId,
        correct_item_type: item.item_type,
        correct_item_id: item.id
      });
    } catch (err) {
      console.warn('Correction log failed:', err.message);
    }
  }

  // Clear previous scan and navigate to result
  sessionStorage.removeItem('scanResult');
  sessionStorage.removeItem('scanImage');

  location.href = `result.html?type=${item.item_type}&id=${item.id}`;
}