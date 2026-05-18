window.onload = async function () {
  const auth = requireAuth(['participant', 'mentor']);
  if (!auth) return;
  setupLogout();
  setupNav();

  const { res, data } = await apiFetch('/api/projects/');
  const list = document.getElementById('projects-list');
  const formSection = document.getElementById('project-form-section');

  if (!res.ok) {
    list.textContent = apiDetail(data);
    if (formSection) formSection.style.display = 'none';
    return;
  }

  if (!data.length) {
    list.innerHTML = '<p class="muted">No projects yet.</p>';
  } else {
    list.innerHTML = data
      .map((p) => {
        const submitBtn =
          auth.role === 'participant' && p.status === 'draft'
            ? `<button type="button" onclick="finalizeProject(${p.project_id})">Mark as submitted</button>`
            : `<span class="badge">${p.status}</span>`;
        return `
      <div class="card">
        <strong>${p.title}</strong> — ${p.team_name} (${p.event_name})<br>
        <p>${p.description || ''}</p>
        <p class="muted">Project #${p.project_id} · Team #${p.team_id} · ${p.status}</p>
        ${p.repo_link ? `<a href="${p.repo_link}" target="_blank">Repository</a>` : ''}
        ${p.demo_link ? ` · <a href="${p.demo_link}" target="_blank">Demo</a>` : ''}
        <div class="row-actions">${submitBtn}</div>
      </div>`;
      })
      .join('');
  }

  if (auth.role === 'participant') {
    await setupProjectForm(auth);
  } else if (formSection) {
    formSection.style.display = 'none';
  }
};

async function setupProjectForm(auth) {
  const formSection = document.getElementById('project-form-section');
  if (!formSection || auth.role !== 'participant') return;

  const teamsRes = await apiFetch('/api/teams/my');
  const leaderTeams =
    teamsRes.res.ok && Array.isArray(teamsRes.data)
      ? teamsRes.data.filter((t) => t.leader_id === auth.userId)
      : [];

  if (!leaderTeams.length) {
    formSection.innerHTML =
      '<p class="muted">Only team leaders can create projects. Create a team or become leader first.</p>';
    return;
  }

  const select = document.getElementById('team-id');
  select.innerHTML = leaderTeams
    .map((t) => `<option value="${t.team_id}">${t.team_name} (${t.event_name})</option>`)
    .join('');

  document.getElementById('submit-project-form').onsubmit = async (e) => {
    e.preventDefault();
    const errorDiv = document.getElementById('project-error');
    errorDiv.textContent = '';
    const { res, data } = await apiFetch('/api/projects/', {
      method: 'POST',
      body: JSON.stringify({
        team_id: parseInt(document.getElementById('team-id').value, 10),
        title: document.getElementById('project-title').value,
        description: document.getElementById('project-description').value,
        repo_link: document.getElementById('repo-link').value || null,
        demo_link: document.getElementById('demo-link').value || null,
      }),
    });
    if (res.ok) {
      alert('Project created as draft. Submit it when ready.');
      window.location.reload();
    } else {
      errorDiv.textContent = apiDetail(data);
    }
  };
}

async function finalizeProject(projectId) {
  if (!confirm('Submit this project for judging? You can still edit only before judges evaluate.')) return;
  const { res, data } = await apiFetch(`/api/projects/${projectId}`, {
    method: 'PUT',
    body: JSON.stringify({ status: 'submitted' }),
  });
  alert(res.ok ? 'Project submitted!' : apiDetail(data));
  if (res.ok) window.location.reload();
}
