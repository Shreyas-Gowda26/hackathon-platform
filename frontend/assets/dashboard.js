window.onload = function () {
  const auth = requireAuth();
  if (!auth) return;
  setupLogout();
  setupNav();

  const roleInfo = document.getElementById('role-info');
  const quickLinks = document.getElementById('quick-links');
  const roleLabel = auth.role.charAt(0).toUpperCase() + auth.role.slice(1);

  roleInfo.innerHTML = `<p>Logged in as <strong>${roleLabel}</strong> (User #${auth.userId || '—'})</p>`;

  const links = {
    participant: [
      ['events.html', 'Browse & register for events'],
      ['teams.html', 'Manage teams & invites'],
      ['projects.html', 'Your team projects'],
      ['leaderboard.html', 'View leaderboards'],
    ],
    mentor: [
      ['mentors.html', 'Your assigned teams'],
      ['projects.html', 'Mentored team projects'],
      ['leaderboard.html', 'View leaderboards'],
    ],
    judge: [
      ['evaluations.html', 'Assigned teams & evaluations'],
      ['leaderboard.html', 'View leaderboards'],
    ],
    admin: [
      ['admin.html', 'Admin panel (events, assignments)'],
      ['events.html', 'View events'],
      ['leaderboard.html', 'View leaderboards'],
    ],
  };

  const items = links[auth.role] || [];
  quickLinks.innerHTML =
    '<ul class="link-list">' +
    items.map(([href, label]) => `<li><a href="${href}">${label}</a></li>`).join('') +
    '</ul>';
};
