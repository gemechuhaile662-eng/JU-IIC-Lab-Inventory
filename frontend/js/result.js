// =========================================================
// result.js — Render recognition result
// =========================================================

const main = document.getElementById('resultMain');

// ---------- Load data from sessionStorage or URL ----------
const urlParams = new URLSearchParams(location.search);
const manualType = urlParams.get('type');
const manualId = urlParams.get('id');

async function init() {
  if (manualType && manualId) {
    // Manual pick — fetch item details
    try {
      const item = await api.get(`/api/items/${manualType}/${manualId}`);
      renderResult(item, null);
    } catch (err) {
      main.innerHTML = `<div class="actions"><p>Could not load item: ${err.message}</p></div>`;
    }
    return;
  }

  const result = JSON.parse(sessionStorage.getItem('scanResult') || 'null');
  const image = sessionStorage.getItem('scanImage');

  if (!result) {
    location.href = 'camera.html';
    return;
  }

  renderResult(result, image);
}

// ---------- Render success ----------
function renderResult(r, imageDataUrl) {
  const confidencePct = Math.round((r.confidence || 0) * 100);

  // Low confidence / unknown
  if (r.result_status === 'low_confidence' || r.result_status === 'unknown_item') {
    main.innerHTML = renderNotRecognized(r, imageDataUrl, confidencePct);
    return;
  }

  main.innerHTML = `
    <div class="photo-wrap">
      ${imageDataUrl ? `<img src="${imageDataUrl}" alt="Scanned item" class="photo">` : ''}
      <div class="confidence-badge ${r.confidence >= 0.85 ? 'high' : 'med'}">
        ${confidencePct}% match
      </div>
    </div>

    <div class="info-card">
      <h1>${r.display_name || 'Unknown Item'}</h1>
      <p class="category">${r.item_type === 'equipment' ? 'Equipment' : 'Component'}</p>

      <dl class="info-grid">
        ${r.lab_name ? `<dt>Location</dt><dd>${r.lab_name}</dd>` : ''}
        ${r.quantity != null
          ? `<dt>In stock</dt>
             <dd class="${r.low_stock ? 'low' : ''}">
               ${r.quantity} ${r.unit || ''}
               ${r.low_stock ? '<span class="badge-low">LOW</span>' : ''}
             </dd>`
          : ''}
        ${r.supplier_name ? `<dt>Supplier</dt><dd>${r.supplier_name}</dd>` : ''}
        ${r.unit_price != null ? `<dt>Unit price</dt><dd>${formatMoney(r.unit_price)}</dd>` : ''}
        ${r.status ? `<dt>Status</dt><dd>${humanize(r.status)}</dd>` : ''}
        ${r.serial_no ? `<dt>Serial</dt><dd>${r.serial_no}</dd>` : ''}
        ${r.asset_tag ? `<dt>Asset tag</dt><dd>${r.asset_tag}</dd>` : ''}
        ${r.last_txn_date ? `<dt>Last movement</dt><dd>${formatDate(r.last_txn_date)}</dd>` : ''}
            </dl>
    </div>

    <!-- QR CODE SECTION -->
    <div class="info-card" style="margin-top: 12px; text-align: center;">
      <h3 style="font-size: 14px; color: var(--muted); text-transform: uppercase; margin-bottom: 12px;">QR Code</h3>
      <img
        src="${API_BASE}/api/items/${r.item_type}/${r.item_id}/qr"
        alt="QR code"
        style="width: 180px; height: 180px; border: 1px solid var(--border); border-radius: 8px;"
      >
      <p style="font-size: 12px; color: var(--muted); margin-top: 8px;">
        Scan this to open this item
      </p>
      <a
        href="${API_BASE}/api/items/${r.item_type}/${r.item_id}/qr"
        download="qr-${r.item_type}-${r.item_id}.png"
        class="btn"
        style="display: inline-block; margin-top: 12px; padding: 10px 20px; text-decoration: none;"
      >
        Download QR
      </a>
    </div>

    <div class="actions">
  `;
}

// ---------- Render not recognized ----------
function renderNotRecognized(r, imageDataUrl, confidencePct) {
  return `
    <div class="photo-wrap">
      ${imageDataUrl ? `<img src="${imageDataUrl}" alt="Scanned item" class="photo">` : ''}
      <div class="confidence-badge low">${confidencePct}% match</div>
    </div>

    <div class="info-card warn">
      <h1>Item not recognized</h1>
      <p>The system isn't sure what this item is. Try one of these:</p>
    </div>

    <div class="actions">
      <button class="btn primary" onclick="location.href='camera.html'">Retake photo</button>
      <button class="btn" onclick="location.href='manual.html'">Pick manually</button>
      <button class="btn ghost" onclick="location.href='manual.html'">Enter code</button>
    </div>
  `;
}

// ---------- Actions ----------
async function borrowItem(itemId) {
  if (!confirm('Are you sure you want to borrow this item for 7 days?')) return;
  try {
    const res = await api.post('/api/borrowings', { equip_id: itemId });
    alert(`✅ Item borrowed successfully!\nDue date: ${res.due_date}`);
    location.href = 'my-borrowings.html';
  } catch (err) {
    alert('❌ Failed to borrow: ' + err.message);
  }
}

function reportWrong() {
  const result = JSON.parse(sessionStorage.getItem('scanResult') || 'null');
  if (!result || !result.log_id) {
    location.href = 'manual.html';
    return;
  }
  location.href = `manual.html?correct_log=${result.log_id}`;
}

// ---------- Helpers ----------
const formatMoney = (n) =>
  'ETB ' + Number(n).toLocaleString('en-US', { minimumFractionDigits: 2 });

const formatDate = (d) => new Date(d).toLocaleDateString();

const humanize = (s) =>
  s.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());

// ---------- Run ----------
init();