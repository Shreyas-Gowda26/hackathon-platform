window.onload = async function () {
  const auth = requireAuth(['participant', 'admin']);
  if (!auth) return;
  setupLogout();
  setupNav();

  const eventsList = document.getElementById('events-list');
  const { res, data } = await apiFetch('/api/events/');

  if (!res.ok) {
    eventsList.textContent = apiDetail(data);
    return;
  }
  if (!data.length) {
    eventsList.textContent = 'No events found.';
    return;
  }

  eventsList.innerHTML = data
    .map(
      (ev) => `
    <div class="card">
      <strong>${ev.event_name}</strong> <span class="badge">${ev.status || 'upcoming'}</span><br>
      <span>${ev.description || ''}</span><br>
      <small>${formatDate(ev.start_date)} to ${formatDate(ev.end_date)}</small><br>
      <button type="button" onclick="registerEvent(${ev.event_id})">Register</button>
    </div>`
    )
    .join('');
};

async function registerEvent(eventId) {
  const { res, data } = await apiFetch('/api/registrations/', {
    method: 'POST',
    body: JSON.stringify({ event_id: eventId }),
  });
  alert(res.ok ? 'Registered successfully!' : apiDetail(data));
}
