// index.js: Handles login and registration
const loginForm = document.getElementById('login-form');
const registerForm = document.getElementById('register-form');

loginForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const email = document.getElementById('login-email').value;
  const password = document.getElementById('login-password').value;
  const errorDiv = document.getElementById('login-error');
  errorDiv.textContent = '';
  try {
    const res = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    const data = await res.json();
    if (res.ok) {
      localStorage.setItem('token', data.access_token);
      localStorage.setItem('role', data.role);
      localStorage.setItem('user_id', String(data.user_id));
      window.location.href = 'dashboard.html';
    } else {
      errorDiv.textContent = data.detail || 'Login failed.';
    }
  } catch (err) {
    errorDiv.textContent = 'Server error.';
  }
});

registerForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const name = document.getElementById('register-name').value;
  const email = document.getElementById('register-email').value;
  const phone = document.getElementById('register-phone').value;
  const role = document.getElementById('register-role').value;
  const password = document.getElementById('register-password').value;
  const errorDiv = document.getElementById('register-error');
  const successDiv = document.getElementById('register-success');
  errorDiv.textContent = '';
  successDiv.textContent = '';
  try {
    const res = await fetch('/api/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, email, phone, role, password })
    });
    const data = await res.json();
    if (res.ok) {
      successDiv.textContent = 'Registration successful! Please login.';
      registerForm.reset();
    } else {
      errorDiv.textContent = data.detail || 'Registration failed.';
    }
  } catch (err) {
    errorDiv.textContent = 'Server error.';
  }
});
