window.onload = async function () {
  const auth = requireAuth(['judge']);
  if (!auth) return;
  setupLogout();
  setupNav();

  await loadAssignedTeams();
  await loadProjectsToEvaluate();
};

async function loadAssignedTeams() {
  const box = document.getElementById('assigned-teams');
  const { res, data } = await apiFetch('/api/judges/my-teams');

  if (!res.ok) {
    box.innerHTML = `<p class="error">${apiDetail(data)}</p>`;
    return;
  }

  if (!Array.isArray(data) || !data.length) {
    box.innerHTML =
      '<p class="muted">No teams assigned yet. Ask an admin to assign you to teams from the Admin panel.</p>';
    return;
  }

  box.innerHTML = data
    .map((t) => {
      let projectLine = '<span class="muted">No project created yet</span>';
      if (t.project_id) {
        const status = t.project_status || 'draft';
        projectLine = `<strong>${t.project_title}</strong> — <span class="badge">${status}</span>`;
        if (status !== 'submitted') {
          projectLine += ' <span class="muted">(waiting for team to submit)</span>';
        }
      }
      return `
    <div class="card">
      <strong>${t.team_name}</strong> — ${t.event_name}<br>
      Team #${t.team_id} · Leader: ${t.leader_name}<br>
      <span class="muted">${formatDate(t.start_date)} to ${formatDate(t.end_date)}</span><br>
      Project: ${projectLine}
    </div>`;
    })
    .join('');
}

async function loadProjectsToEvaluate() {
  const list = document.getElementById('projects-to-evaluate');
  const { res, data } = await apiFetch('/api/projects/');

  if (!res.ok) {
    list.innerHTML = `<p class="error">${apiDetail(data)}</p>`;
    return;
  }

  if (!Array.isArray(data) || !data.length) {
    list.innerHTML =
      '<p class="muted">No submitted projects yet. Check back after teams submit their work.</p>';
    return;
  }

  list.innerHTML = data
    .map(
      (p) => `
    <div class="card" id="project-card-${p.project_id}">
      <strong>${p.title}</strong> — ${p.team_name} (${p.event_name})<br>
      <p>${p.description || ''}</p>
      <p class="muted">Project #${p.project_id} · Team #${p.team_id}</p>
      ${p.repo_link ? `<a href="${p.repo_link}" target="_blank">Repository</a>` : ''}
      ${p.demo_link ? ` · <a href="${p.demo_link}" target="_blank">Demo</a>` : ''}
      <div class="inline-form-grid" style="margin-top:1rem">
        <input type="number" id="score-${p.project_id}" placeholder="Score 0-100" min="0" max="100">
        <input type="text" id="feedback-${p.project_id}" placeholder="Feedback">
        <button type="button" onclick="submitEvaluation(${p.project_id})">Submit score</button>
      </div>
      <div class="error" id="eval-error-${p.project_id}"></div>
    </div>`
    )
    .join('');
}

async function submitEvaluation(projectId) {
  const score = document.getElementById(`score-${projectId}`).value;
  const feedback = document.getElementById(`feedback-${projectId}`).value;
  const errorDiv = document.getElementById(`eval-error-${projectId}`);
  errorDiv.textContent = '';

  const { res, data } = await apiFetch('/api/evaluations/', {
    method: 'POST',
    body: JSON.stringify({
      project_id: projectId,
      score: parseFloat(score),
      feedback,
    }),
  });

  if (res.ok) {
    alert('Evaluation submitted!');
    window.location.reload();
  } else {
    errorDiv.textContent = apiDetail(data);
  }
}
