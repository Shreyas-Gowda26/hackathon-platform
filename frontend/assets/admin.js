window.onload = async function () {
  const auth = requireAuth(['admin']);
  if (!auth) return;
  setupLogout();
  setupNav();

  await loadUsers();
  await loadEventsWithTeams();
  await loadMentorAssignments();
  await loadJudgeAssignments();

  document.getElementById('create-event-form').onsubmit = onCreateEvent;
  document.getElementById('assign-mentor-form').onsubmit = onAssignMentor;
  document.getElementById('assign-judge-form').onsubmit = onAssignJudge;
};

async function onCreateEvent(e) {
  e.preventDefault();
  const errorDiv = document.getElementById('event-error');
  errorDiv.textContent = '';
  const { res, data } = await apiFetch('/api/events/', {
    method: 'POST',
    body: JSON.stringify({
      event_name: document.getElementById('event-name').value,
      description: document.getElementById('event-description').value,
      start_date: document.getElementById('start-date').value,
      end_date: document.getElementById('end-date').value,
      max_team_size: parseInt(document.getElementById('max-team-size').value, 10),
      min_team_size: parseInt(document.getElementById('min-team-size').value, 10),
    }),
  });
  if (res.ok) {
    alert('Event created!');
    window.location.reload();
  } else {
    errorDiv.textContent = apiDetail(data);
  }
}

async function onAssignMentor(e) {
  e.preventDefault();
  const errorDiv = document.getElementById('mentor-assign-error');
  errorDiv.textContent = '';
  const { res, data } = await apiFetch('/api/mentors/assign', {
    method: 'POST',
    body: JSON.stringify({
      mentor_id: parseInt(document.getElementById('mentor-id').value, 10),
      team_id: parseInt(document.getElementById('mentor-team-id').value, 10),
    }),
  });
  if (res.ok) {
    alert(data.message || 'Mentor assigned');
    e.target.reset();
    await loadMentorAssignments();
  } else {
    errorDiv.textContent = apiDetail(data);
  }
}

async function onAssignJudge(e) {
  e.preventDefault();
  const errorDiv = document.getElementById('judge-assign-error');
  errorDiv.textContent = '';
  const { res, data } = await apiFetch('/api/judges/assign', {
    method: 'POST',
    body: JSON.stringify({
      judge_id: parseInt(document.getElementById('judge-id').value, 10),
      team_id: parseInt(document.getElementById('judge-team-id').value, 10),
    }),
  });
  if (res.ok) {
    alert(data.message || 'Judge assigned');
    e.target.reset();
    await loadJudgeAssignments();
  } else {
    errorDiv.textContent = apiDetail(data);
  }
}

async function loadUsers() {
  const list = document.getElementById('users-list');
  const { res, data } = await apiFetch('/api/users/');
  if (!res.ok) {
    list.textContent = apiDetail(data);
    return;
  }
  list.innerHTML = `
    <table class="data-table">
      <thead><tr><th>ID</th><th>Name</th><th>Role</th><th>Email</th></tr></thead>
      <tbody>
        ${data.map((u) => `<tr><td>${u.user_id}</td><td>${u.name}</td><td>${u.role}</td><td>${u.email}</td></tr>`).join('')}
      </tbody>
    </table>`;
}

async function loadEventsWithTeams() {
  const list = document.getElementById('events-admin-list');
  const { res, data } = await apiFetch('/api/events/');
  if (!res.ok) {
    list.textContent = apiDetail(data);
    return;
  }
  const parts = [];
  for (const ev of data) {
    const teamsRes = await apiFetch(`/api/teams/event/${ev.event_id}`);
    const teams = teamsRes.res.ok && Array.isArray(teamsRes.data) ? teamsRes.data : [];
    parts.push(`
      <div class="subcard">
        <strong>${ev.event_name}</strong> (Event #${ev.event_id}, ${ev.status})
        <p class="muted">${formatDate(ev.start_date)} – ${formatDate(ev.end_date)}</p>
        <ul>
          ${teams.map((t) => `<li>Team #${t.team_id}: ${t.team_name} — leader ${t.leader_name} (user #${t.leader_id})</li>`).join('') || '<li>No teams yet</li>'}
        </ul>
      </div>`);
  }
  list.innerHTML = parts.join('') || '<p class="muted">No events.</p>';
}

async function loadMentorAssignments() {
  const list = document.getElementById('mentor-assignments-list');
  const { res, data } = await apiFetch('/api/mentors/assignments');
  if (!res.ok) {
    list.innerHTML = `<p class="error">${apiDetail(data)}</p>`;
    return;
  }
  if (!Array.isArray(data) || !data.length) {
    list.innerHTML = '<p class="muted">No mentor assignments.</p>';
    return;
  }
  list.innerHTML = `
    <table class="data-table">
      <thead><tr><th>Mentor</th><th>Team</th><th>Event</th><th></th></tr></thead>
      <tbody>
        ${data.map((a) => `
          <tr>
            <td>#${a.mentor_id} ${a.mentor_name}</td>
            <td>#${a.team_id} ${a.team_name}</td>
            <td>${a.event_name}</td>
            <td><button type="button" class="btn-small btn-secondary" onclick="removeMentor(${a.mentor_id}, ${a.team_id})">Remove</button></td>
          </tr>`).join('')}
      </tbody>
    </table>`;
}

async function loadJudgeAssignments() {
  const list = document.getElementById('judge-assignments-list');
  const { res, data } = await apiFetch('/api/judges/assignments');
  if (!res.ok) {
    list.innerHTML = `<p class="error">${apiDetail(data)}</p>`;
    return;
  }
  if (!Array.isArray(data) || !data.length) {
    list.innerHTML = '<p class="muted">No judge assignments.</p>';
    return;
  }
  list.innerHTML = `
    <table class="data-table">
      <thead><tr><th>Judge</th><th>Team</th><th>Event</th><th></th></tr></thead>
      <tbody>
        ${data.map((a) => `
          <tr>
            <td>#${a.judge_id} ${a.judge_name}</td>
            <td>#${a.team_id} ${a.team_name}</td>
            <td>${a.event_name}</td>
            <td><button type="button" class="btn-small btn-secondary" onclick="removeJudge(${a.judge_id}, ${a.team_id})">Remove</button></td>
          </tr>`).join('')}
      </tbody>
    </table>`;
}

async function removeMentor(mentorId, teamId) {
  if (!confirm('Remove this mentor assignment?')) return;
  const { res, data } = await apiFetch('/api/mentors/remove', {
    method: 'DELETE',
    body: JSON.stringify({ mentor_id: mentorId, team_id: teamId }),
  });
  alert(res.ok ? 'Removed' : apiDetail(data));
  if (res.ok) await loadMentorAssignments();
}

async function removeJudge(judgeId, teamId) {
  if (!confirm('Remove this judge assignment?')) return;
  const { res, data } = await apiFetch('/api/judges/remove', {
    method: 'DELETE',
    body: JSON.stringify({ judge_id: judgeId, team_id: teamId }),
  });
  alert(res.ok ? 'Removed' : apiDetail(data));
  if (res.ok) await loadJudgeAssignments();
}
