const API_BASE = '/api';

function getToken() { return localStorage.getItem('crm_token'); }
function getUser() { try { return JSON.parse(localStorage.getItem('crm_user')); } catch { return null; } }
function setAuth(token, user) { localStorage.setItem('crm_token', token); localStorage.setItem('crm_user', JSON.stringify(user)); }
function clearAuth() { localStorage.removeItem('crm_token'); localStorage.removeItem('crm_user'); }

function requireAuth() {
  if (!getToken()) { window.location.href = '/'; return false; }
  return true;
}

async function apiFetch(path, options = {}) {
  const token = getToken();
  const headers = { 'Content-Type': 'application/json', ...options.headers };
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const res = await fetch(API_BASE + path, { ...options, headers });

  if (res.status === 401) { clearAuth(); window.location.href = '/'; return; }

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Request failed (${res.status})`);
  }
  if (res.status === 204) return null;
  return res.json();
}

const api = {
  auth: {
    login: (email, password) => apiFetch('/auth/login', { method: 'POST', body: JSON.stringify({ email, password }) }),
    register: (name, email, password) => apiFetch('/auth/register', { method: 'POST', body: JSON.stringify({ name, email, password }) }),
    me: () => apiFetch('/auth/me'),
  },
  leads: {
    list: (params = {}) => {
      const q = new URLSearchParams(Object.fromEntries(Object.entries(params).filter(([, v]) => v)));
      return apiFetch('/leads' + (q.toString() ? '?' + q : ''));
    },
    get: (id) => apiFetch(`/leads/${id}`),
    create: (data) => apiFetch('/leads', { method: 'POST', body: JSON.stringify(data) }),
    update: (id, data) => apiFetch(`/leads/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
    delete: (id) => apiFetch(`/leads/${id}`, { method: 'DELETE' }),
  },
  calls: {
    log: (data) => apiFetch('/calls', { method: 'POST', body: JSON.stringify(data) }),
    forLead: (leadId) => apiFetch(`/calls/lead/${leadId}`),
    list: () => apiFetch('/calls'),
  },
  dashboard: {
    stats: () => apiFetch('/dashboard/stats'),
  },
};

// ── UI Helpers ──────────────────────────────────────────────────────────────

function showToast(msg, type = '') {
  const t = document.createElement('div');
  t.className = `toast ${type}`;
  t.textContent = msg;
  document.body.appendChild(t);
  setTimeout(() => t.remove(), 3200);
}

function scoreClass(score) {
  if (score >= 70) return 'hot';
  if (score >= 40) return 'warm';
  return 'cold';
}

function scoreBar(score) {
  const cls = scoreClass(score);
  return `<div class="score-wrap">
    <div class="score-bar"><div class="score-fill ${cls}" style="width:${score}%"></div></div>
    <span class="score-num ${cls}">${score}</span>
  </div>`;
}

function statusBadge(status) {
  return `<span class="badge badge-${status}">${status}</span>`;
}

function fmtDate(dt) {
  if (!dt) return '—';
  return new Date(dt).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

function fmtDateTime(dt) {
  if (!dt) return '—';
  return new Date(dt).toLocaleString('en-US', { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' });
}

function fmtDuration(sec) {
  if (!sec) return '—';
  const m = Math.floor(sec / 60), s = sec % 60;
  return `${m}m ${s.toString().padStart(2, '0')}s`;
}

function fmtMoney(val) {
  if (!val) return '—';
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(val);
}

const outcomeLabel = { answered: 'Answered', voicemail: 'Left Voicemail', no_answer: 'No Answer', scheduled_callback: 'Scheduled Callback' };
const outcomeEmoji = { answered: '✅', voicemail: '📬', no_answer: '📵', scheduled_callback: '📅' };

function logout() { clearAuth(); window.location.href = '/'; }

function setUserUI() {
  const user = getUser();
  if (!user) return;
  const el = document.getElementById('userName');
  if (el) el.textContent = user.name;
}
