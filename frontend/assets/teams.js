window.onload = async function () {
  const auth = requireAuth(['participant', 'admin']);
  if (!auth) return;
  setupLogout();
  setupNav();

  await loadInvites(auth);
  await loadTeams(auth);
  await loadEventsForCreate(auth);

  document.getElementById('create-team-form').onsubmit = async (e) => {
    e.preventDefault();
    const errorDiv = document.getElementById('team-error');
    errorDiv.textContent = '';
    const { res, data } = await apiFetch('/api/teams/', {
      method: 'POST',
      body: JSON.stringify({
        team_name: document.getElementById('team-name').value,
        event_id: parseInt(document.getElementById('event-id').value, 10),
      }),
    });
    if (res.ok) {
      alert('Team created!');
      window.location.reload();
    } else {
      errorDiv.textContent = apiDetail(data);
    }
  };
};

async function loadEventsForCreate(auth) {
  const select = document.getElementById('event-id');
  if (!select) return;
  const { res, data } = await apiFetch('/api/registrations/my');
  if (!res.ok || !Array.isArray(data)) return;
  select.innerHTML =
    '<option value="">Select registered event</option>' +
    data
      .map(
        (r) =>
          `<option value="${r.event_id}">${r.event_name} (${r.status})</option>`
      )
      .join('');
}

async function loadInvites(auth) {
  const box = document.getElementById('invites-list');
  if (!box) return;
  const { res, data } = await apiFetch('/api/teams/my-invites');
  if (!res.ok) {
    box.textContent = apiDetail(data);
    return;
  }
  if (!data.length) {
    box.innerHTML = '<p class="muted">No pending invites.</p>';
    return;
  }
  box.innerHTML = data
    .map(
      (inv) => `
    <div class="card">
      <strong>${inv.team_name}</strong> — ${inv.event_name}<br>
      Invited by ${inv.invited_by_name}
      <div class="row-actions">
        <button type="button" onclick="respondInvite(${inv.id}, 'accepted')">Accept</button>
        <button type="button" class="btn-secondary" onclick="respondInvite(${inv.id}, 'rejected')">Decline</button>
      </div>
    </div>`
    )
    .join('');
}

async function respondInvite(memberId, status) {
  const { res, data } = await apiFetch(`/api/teams/invites/${memberId}/respond`, {
    method: 'PUT',
    body: JSON.stringify({ status }),
  });
  alert(res.ok ? data.message || 'Done' : apiDetail(data));
  if (res.ok) window.location.reload();
}

async function loadTeams(auth) {
  const list = document.getElementById('teams-list');
  const { res, data } = await apiFetch('/api/teams/my');
  if (!res.ok) {
    list.textContent = apiDetail(data);
    return;
  }
  if (!Array.isArray(data) || !data.length) {
    list.innerHTML = '<p class="muted">No teams yet. Register for an event and create one.</p>';
    return;
  }

  const cards = [];
  for (const team of data) {
    const isLeader = team.leader_id === auth.userId;
    const detail = await apiFetch(`/api/teams/${team.team_id}`);
    const members =
      detail.res.ok && detail.data.members
        ? detail.data.members
        : [];
    const accepted = members.filter((m) => m.status === 'accepted');
    const pending = members.filter((m) => m.status === 'pending');

    let html = `
      <div class="card">
        <strong>${team.team_name}</strong> — ${team.event_name}
        <span class="badge">${isLeader ? 'Leader' : 'Member'}</span>
        <p class="muted">Team ID: ${team.team_id} · Event ID: ${team.event_id}</p>
        <h4>Members (${accepted.length})</h4>
        <ul>${accepted.map((m) => `<li>#${m.user_id} ${m.name} (${m.role})</li>`).join('') || '<li>None</li>'}</ul>`;

    if (pending.length) {
      html += `<h4>Pending invites</h4><ul>${pending.map((m) => `<li>#${m.user_id} ${m.name}</li>`).join('')}</ul>`;
    }

    if (isLeader) {
      html += `
        <h4>Add member by User ID</h4>
        <div class="inline-form">
          <input type="number" id="member-user-${team.team_id}" placeholder="User ID" min="1">
          <button type="button" onclick="addMember(${team.team_id})">Add member</button>
        </div>
        <p class="hint">User must be registered for this event and not on another team.</p>
        <div class="error" id="member-error-${team.team_id}"></div>`;
    }

    html += '</div>';
    cards.push(html);
  }
  list.innerHTML = cards.join('');
}

async function addMember(teamId) {
  const input = document.getElementById(`member-user-${teamId}`);
  const errorDiv = document.getElementById(`member-error-${teamId}`);
  const userId = parseInt(input.value, 10);
  if (!userId) {
    errorDiv.textContent = 'Enter a valid user ID.';
    return;
  }
  errorDiv.textContent = '';
  const { res, data } = await apiFetch(`/api/teams/${teamId}/members`, {
    method: 'POST',
    body: JSON.stringify({ user_id: userId }),
  });
  if (res.ok) {
    alert(data.message || 'Member added');
    window.location.reload();
  } else {
    errorDiv.textContent = apiDetail(data);
  }
}
