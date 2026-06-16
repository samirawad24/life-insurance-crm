// Redirect if already logged in
if (getToken()) window.location.href = '/dashboard.html';

function toggleForm() {
  const login = document.getElementById('loginForm');
  const reg = document.getElementById('registerForm');
  const showing = login.style.display !== 'none';
  login.style.display = showing ? 'none' : '';
  reg.style.display = showing ? '' : 'none';
  document.getElementById('authError').classList.remove('show');
}

function showError(msg) {
  const el = document.getElementById('authError');
  el.textContent = msg;
  el.classList.add('show');
}

async function login() {
  const email = document.getElementById('loginEmail').value.trim();
  const password = document.getElementById('loginPassword').value;
  if (!email || !password) { showError('Please fill in all fields.'); return; }
  try {
    const data = await api.auth.login(email, password);
    setAuth(data.access_token, data.user);
    window.location.href = '/dashboard.html';
  } catch (e) {
    showError(e.message);
  }
}

async function register() {
  const name = document.getElementById('regName').value.trim();
  const email = document.getElementById('regEmail').value.trim();
  const password = document.getElementById('regPassword').value;
  if (!name || !email || !password) { showError('Please fill in all fields.'); return; }
  if (password.length < 6) { showError('Password must be at least 6 characters.'); return; }
  try {
    const data = await api.auth.register(name, email, password);
    setAuth(data.access_token, data.user);
    window.location.href = '/dashboard.html';
  } catch (e) {
    showError(e.message);
  }
}

document.addEventListener('keydown', e => {
  if (e.key !== 'Enter') return;
  if (document.getElementById('registerForm').style.display !== 'none') register();
  else login();
});
