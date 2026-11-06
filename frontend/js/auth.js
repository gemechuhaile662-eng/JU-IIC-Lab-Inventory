// =========================================================
// js/auth.js — Shared authentication helpers
// Must be loaded AFTER api.js
// =========================================================

async function requireAuth() {
  try {
    const me = await api.get('/api/auth/me');
    sessionStorage.setItem('user', JSON.stringify(me));
    return me;
  } catch (err) {
    if (err.status === 401) {
      location.href = 'login.html';
      throw new Error('not authenticated');
    }
    throw err;
  }
}

function getCurrentUser() {
  try {
    return JSON.parse(sessionStorage.getItem('user') || 'null');
  } catch {
    return null;
  }
}

function initials(name) {
  if (!name) return '?';
  return name
    .split(' ')
    .map((p) => p[0])
    .slice(0, 2)
    .join('')
    .toUpperCase();
}

function renderUserChip(elementId = 'userChip') {
  const el = document.getElementById(elementId);
  const user = getCurrentUser();
  if (!el || !user) return;

  el.innerHTML = `
    <span class="avatar">${initials(user.full_name)}</span>
    <span class="user-name">${user.full_name}</span>
  `;
  el.title = `${user.full_name} (${user.role})`;
}

async function logout() {
  try {
    await api.post('/api/auth/logout', {});
  } catch (e) {}
  sessionStorage.clear();
  location.href = 'index.html';
}

// ---------- Toast helper (used by all pages) ----------
function showToast(message, type = 'info', duration = 2500) {
  let t = document.getElementById('appToast');
  if (!t) {
    t = document.createElement('div');
    t.id = 'appToast';
    t.className = 'toast';
    document.body.appendChild(t);
  }
  t.textContent = message;
  t.className = 'toast ' + type;
  // force reflow
  void t.offsetWidth;
  t.classList.add('show');
  clearTimeout(t._timer);
  t._timer = setTimeout(() => t.classList.remove('show'), duration);
}