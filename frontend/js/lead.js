if (!requireAuth()) { /* redirected */ }
setUserUI();

const params = new URLSearchParams(window.location.search);
const leadId = parseInt(params.get('id'));
if (!leadId) window.location.href = '/leads.html';

let currentLead = null;

async function loadLead() {
  try {
    currentLead = await api.leads.get(leadId);
    populateForm(currentLead);
    await loadCalls();
  } catch (e) {
    showToast('Failed to load lead: ' + e.message, 'error');
  }
}

function populateForm(lead) {
  const name = `${lead.first_name} ${lead.last_name}`;
  document.title = `${name} — Insurance CRM`;
  document.getElementById('headerName').textContent = name;
  document.getElementById('leadName').textContent = name;

  const contact = [lead.phone, lead.email].filter(Boolean).join(' · ');
  document.getElementById('leadMeta').textContent = contact || 'No contact info';
  document.getElementById('leadStatusBadge').innerHTML = statusBadge(lead.status);

  const cls = scoreClass(lead.score);
  const circle = document.getElementById('scoreCircle');
  circle.textContent = lead.score;
  circle.className = `score-circle ${cls}`;

  document.getElementById('eFirstName').value = lead.first_name || '';
  document.getElementById('eLastName').value = lead.last_name || '';
  document.getElementById('ePhone').value = lead.phone || '';
  document.getElementById('eEmail').value = lead.email || '';
  document.getElementById('eAge').value = lead.age || '';
  document.getElementById('eIncome').value = lead.annual_income || '';
  document.getElementById('eCoverage').value = lead.coverage_amount || '';
  document.getElementById('eHealth').value = lead.health_status || '';
  document.getElementById('eStatus').value = lead.status;
  document.getElementById('eSource').value = lead.source;
  document.getElementById('eNotes').value = lead.notes || '';
}

async function saveChanges() {
  const data = {
    first_name: document.getElementById('eFirstName').value.trim() || undefined,
    last_name: document.getElementById('eLastName').value.trim() || undefined,
    phone: document.getElementById('ePhone').value.trim() || null,
    email: document.getElementById('eEmail').value.trim() || null,
    age: parseInt(document.getElementById('eAge').value) || null,
    annual_income: parseFloat(document.getElementById('eIncome').value) || null,
    coverage_amount: parseFloat(document.getElementById('eCoverage').value) || null,
    health_status: document.getElementById('eHealth').value || null,
    status: document.getElementById('eStatus').value,
    source: document.getElementById('eSource').value,
    notes: document.getElementById('eNotes').value.trim() || null,
  };
  try {
    currentLead = await api.leads.update(leadId, data);
    populateForm(currentLead);
    showToast('Saved', 'success');
  } catch (e) {
    showToast('Error: ' + e.message, 'error');
  }
}

async function loadCalls() {
  try {
    const calls = await api.calls.forLead(leadId);
    const el = document.getElementById('callLog');
    if (!calls.length) {
      el.innerHTML = '<div class="empty-state"><div class="empty-icon">📞</div><p>No calls logged yet</p></div>';
      return;
    }
    el.innerHTML = calls.map(c => `
      <div class="call-item">
        <div class="call-icon">${outcomeEmoji[c.outcome] || '📞'}</div>
        <div class="call-details">
          <div class="call-outcome">${outcomeLabel[c.outcome] || c.outcome}</div>
          ${c.notes ? `<div class="call-notes">${c.notes}</div>` : ''}
          <div class="call-time">${fmtDateTime(c.called_at)}${c.duration_seconds ? ' · ' + fmtDuration(c.duration_seconds) : ''}</div>
        </div>
      </div>
    `).join('');
  } catch (e) {
    showToast('Failed to load calls', 'error');
  }
}

function openCallModal() {
  document.getElementById('callModal').classList.add('show');
  document.getElementById('cOutcome').focus();
}

function closeCallModal() {
  document.getElementById('callModal').classList.remove('show');
  document.getElementById('cDuration').value = '';
  document.getElementById('cNotes').value = '';
  document.getElementById('cOutcome').value = 'answered';
}

async function submitCall() {
  const outcome = document.getElementById('cOutcome').value;
  const mins = parseFloat(document.getElementById('cDuration').value) || 0;
  const notes = document.getElementById('cNotes').value.trim();
  try {
    await api.calls.log({ lead_id: leadId, outcome, duration_seconds: Math.round(mins * 60), notes: notes || null });
    showToast('Call logged', 'success');
    closeCallModal();
    await loadLead();
  } catch (e) {
    showToast('Error: ' + e.message, 'error');
  }
}

async function confirmDelete() {
  const name = currentLead ? `${currentLead.first_name} ${currentLead.last_name}` : 'this lead';
  if (!confirm(`Delete ${name}? This cannot be undone.`)) return;
  try {
    await api.leads.delete(leadId);
    showToast('Lead deleted', 'success');
    setTimeout(() => window.location.href = '/leads.html', 600);
  } catch (e) {
    showToast('Error: ' + e.message, 'error');
  }
}

loadLead();
