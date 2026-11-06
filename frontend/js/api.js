// =========================================================
// js/api.js — Fetch wrapper
// =========================================================

const API_BASE = window.API_BASE || 'http://localhost:8000';
const MOCK_MODE = false;

const api = {
  // ---------- GET ----------
  async get(path) {
    const r = await fetch(API_BASE + path, {
      method: 'GET',
      credentials: 'include',
    });
    return handleResponse(r);
  },

  // ---------- POST (JSON) ----------
  async post(path, body) {
    const r = await fetch(API_BASE + path, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify(body || {}),
    });
    return handleResponse(r);
  },

  // ---------- PUT (JSON) ----------
  async put(path, body) {
    const r = await fetch(API_BASE + path, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify(body || {}),
    });
    return handleResponse(r);
  },

  // ---------- POST (multipart / file upload) ----------
  async postForm(path, formData) {
    const r = await fetch(API_BASE + path, {
      method: 'POST',
      credentials: 'include',
      body: formData,
    });
    return handleResponse(r);
  },
};

// =========================================================
// Response handler — parses JSON, throws readable errors
// =========================================================
async function handleResponse(r) {
  const text = await r.text();
  let data = null;

  if (text) {
    try {
      data = JSON.parse(text);
    } catch (e) {
      data = text;
    }
  }

  if (!r.ok) {
    const msg =
      (data && data.error) ||
      (typeof data === 'string' ? data : null) ||
      `HTTP ${r.status}`;

    const err = new Error(msg);
    err.status = r.status;
    err.body = data;
    throw err;
  }

  return data;
}