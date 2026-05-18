window.onload = async function () {
  const auth = requireAuth(['mentor', 'admin']);
  if (!auth) return;
  setupLogout();
  setupNav();

  const assignmentsDiv = document.getElementById('mentor-assignments');
  const heading = document.getElementById('mentors-heading');
  const hint = document.getElementById('mentors-hint');

  if (auth.role === 'admin') {
    if (heading) heading.textContent = 'All mentor assignments';
    if (hint) hint.textContent = 'Overview of mentor–team assignments (as admin).';
    await loadAdminMentorAssignments(assignmentsDiv);
    return;
  }

  if (heading) heading.textContent = 'Your assigned teams';
  if (hint) hint.textContent = 'Teams assigned to you by an admin.';
  await loadMentorTeams(assignmentsDiv);
};

async function loadMentorTeams(assignmentsDiv) {
  const { res, data } = await apiFetch('/api/mentors/my-teams');
  if (!res.ok) {
    assignmentsDiv.textContent = apiDetail(data);
    return;
  }
  if (!Array.isArray(data) || !data.length) {
    assignmentsDiv.innerHTML = '<p class="muted">No teams assigned yet.</p>';
    return;
  }
  assignmentsDiv.innerHTML = data
    .map(
      (a) => `
    <div class="card">
      <strong>${a.team_name}</strong> — ${a.event_name}<br>
      Leader: ${a.leader_name}<br>
      <span class="muted">${formatDate(a.start_date)} to ${formatDate(a.end_date)}</span>
    </div>`
    )
    .join('');
}

async function loadAdminMentorAssignments(assignmentsDiv) {
  const { res, data } = await apiFetch('/api/mentors/assignments');
  if (!res.ok) {
    assignmentsDiv.innerHTML = `<p class="error">${apiDetail(data)}</p>`;
    return;
  }
  if (!Array.isArray(data) || !data.length) {
    assignmentsDiv.innerHTML = '<p class="muted">No mentor assignments yet.</p>';
    return;
  }
  assignmentsDiv.innerHTML = `
    <table class="data-table">
      <thead><tr><th>Mentor</th><th>Team</th><th>Event</th></tr></thead>
      <tbody>
        ${data.map((a) => `
          <tr>
            <td>#${a.mentor_id} ${a.mentor_name}</td>
            <td>#${a.team_id} ${a.team_name}</td>
            <td>${a.event_name}</td>
          </tr>`).join('')}
      </tbody>
    </table>`;
}
