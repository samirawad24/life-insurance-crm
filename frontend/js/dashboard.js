if (!requireAuth()) { /* redirected */ }
setUserUI();

async function loadDashboard() {
  try {
    const s = await api.dashboard.stats();

    document.getElementById('sTotal').textContent = s.total_leads;
    document.getElementById('sNew').textContent = s.new_leads;
    document.getElementById('sQualified').textContent = s.qualified_leads;
    document.getElementById('sConverted').textContent = s.converted_leads;
    document.getElementById('sCalls').textContent = s.calls_today;
    document.getElementById('sRate').textContent = s.conversion_rate + '%';

    document.getElementById('pNew').textContent = s.new_leads;
    document.getElementById('pContacted').textContent = s.contacted_leads;
    document.getElementById('pQualified').textContent = s.qualified_leads;
    document.getElementById('pConverted').textContent = s.converted_leads;
    document.getElementById('pLost').textContent = s.lost_leads;

    const hotEl = document.getElementById('hotLeads');
    if (s.hot_leads.length === 0) {
      hotEl.innerHTML = '<div class="empty-state"><div class="empty-icon">👥</div><p>No leads yet. <a href="/leads.html" style="color:var(--blue)">Add one</a></p></div>';
    } else {
      hotEl.innerHTML = s.hot_leads.map(l => `
        <div class="hot-lead-row" onclick="window.location.href='/lead.html?id=${l.id}'">
          <div>
            <div class="hot-lead-name">${l.first_name} ${l.last_name}</div>
            <div class="hot-lead-sub">${l.phone || l.email || '—'}</div>
          </div>
          <div class="flex items-center gap-2">
            ${statusBadge(l.status)}
            ${scoreBar(l.score)}
          </div>
        </div>
      `).join('');
    }

    const callsEl = document.getElementById('recentCalls');
    if (s.recent_calls.length === 0) {
      callsEl.innerHTML = '<div class="empty-state"><div class="empty-icon">📞</div><p>No calls logged yet</p></div>';
    } else {
      callsEl.innerHTML = s.recent_calls.map(c => `
        <div class="call-item">
          <div class="call-icon">${outcomeEmoji[c.outcome] || '📞'}</div>
          <div class="call-details">
            <div class="call-outcome">${outcomeLabel[c.outcome] || c.outcome}</div>
            ${c.notes ? `<div class="call-notes">${c.notes}</div>` : ''}
            <div class="call-time">${fmtDateTime(c.called_at)}${c.duration_seconds ? ' · ' + fmtDuration(c.duration_seconds) : ''}</div>
          </div>
        </div>
      `).join('');
    }

  } catch (e) {
    showToast('Failed to load dashboard: ' + e.message, 'error');
  }
}

loadDashboard();
