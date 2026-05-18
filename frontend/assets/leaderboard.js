window.onload = async function () {
  requireAuth();
  setupLogout();
  setupNav();

  const select = document.getElementById('event-id');
  const { res, data } = await apiFetch('/api/events/');
  if (res.ok && Array.isArray(data)) {
    select.innerHTML =
      '<option value="">Select event</option>' +
      data.map((e) => `<option value="${e.event_id}">${e.event_name}</option>`).join('');
  }

  select.onchange = () => loadLeaderboard(select.value);
};

async function loadLeaderboard(eventId) {
  const box = document.getElementById('leaderboard-list');
  if (!eventId) {
    box.innerHTML = '';
    return;
  }
  const { res, data } = await apiFetch(`/api/evaluations/leaderboard/${eventId}`);
  if (!res.ok) {
    box.textContent = apiDetail(data);
    return;
  }
  if (!data.length) {
    box.innerHTML = '<p class="muted">No scored projects for this event yet.</p>';
    return;
  }
  box.innerHTML = `
    <table class="data-table">
      <thead>
        <tr><th>Rank</th><th>Team</th><th>Project</th><th>Avg score</th><th>Judges</th></tr>
      </thead>
      <tbody>
        ${data.map((row, i) => `
          <tr>
            <td>${i + 1}</td>
            <td>${row.team_name}</td>
            <td>${row.project_title}</td>
            <td>${row.average_score ?? '—'}</td>
            <td>${row.total_judges}</td>
          </tr>`).join('')}
      </tbody>
    </table>`;
}
