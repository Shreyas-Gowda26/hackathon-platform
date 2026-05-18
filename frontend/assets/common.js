function getAuth() {
  return {
    token: localStorage.getItem('token'),
    role: localStorage.getItem('role'),
    userId: parseInt(localStorage.getItem('user_id'), 10),
  };
}

function apiDetail(data) {
  if (!data) return 'Request failed';
  if (typeof data.detail === 'string') return data.detail;
  if (Array.isArray(data.detail)) {
    return data.detail.map((e) => e.msg || JSON.stringify(e)).join('; ');
  }
  return 'Request failed';
}

async function apiFetch(url, options = {}) {
  const auth = getAuth();
  const headers = { ...(options.headers || {}) };
  if (auth.token) headers.Authorization = 'Bearer ' + auth.token;
  if (options.body && !headers['Content-Type']) {
    headers['Content-Type'] = 'application/json';
  }
  const res = await fetch(url, { ...options, headers });
  let data = null;
  const text = await res.text();
  if (text) {
    try {
      data = JSON.parse(text);
    } catch {
      data = { detail: text };
    }
  }
  return { res, data };
}

function requireAuth(allowedRoles) {
  const auth = getAuth();
  if (!auth.token) {
    window.location.href = 'index.html';
    return null;
  }
  if (allowedRoles && !allowedRoles.includes(auth.role)) {
    window.location.href = 'dashboard.html';
    return null;
  }
  return auth;
}

function setupLogout() {
  const btn = document.getElementById('logout');
  if (btn) {
    btn.onclick = (e) => {
      e.preventDefault();
      localStorage.clear();
      window.location.href = 'index.html';
    };
  }
}

function setupNav() {
  const auth = getAuth();
  const role = auth.role;
  const links = {
    'nav-events': ['participant', 'admin'],
    'nav-teams': ['participant', 'admin'],
    'nav-projects': ['participant', 'admin', 'mentor'],
    'nav-mentors': ['mentor', 'admin'],
    'nav-evaluations': ['judge', 'admin'],
    'nav-admin': ['admin'],
    'nav-leaderboard': ['participant', 'admin', 'judge', 'mentor'],
  };
  Object.entries(links).forEach(([id, roles]) => {
    const el = document.getElementById(id);
    if (el) el.style.display = roles.includes(role) ? '' : 'none';
  });
}

function formatDate(value) {
  if (!value) return '';
  if (typeof value === 'string') return value.slice(0, 10);
  return String(value).slice(0, 10);
}
