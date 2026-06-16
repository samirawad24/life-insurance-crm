if (!requireAuth()) { /* redirected */ }
setUserUI();

let allLeads = [];

async function loadLeads() {
  try {
    allLeads = await api.leads.list();
    renderTable(allLeads);
  } catch (e) {
    showToast('Failed to load leads: ' + e.message, 'error');
  }
}

function filterLeads() {
  const search = document.getElementById('searchInput').value.toLowerCase();
  const status = document.getElementById('statusFilter').value;
  const source = document.getElementById('sourceFilter').value;

  const filtered = allLeads.filter(l => {
    const full = `${l.first_name} ${l.last_name}`.toLowerCase();
    const matchSearch = !search || full.includes(search) || (l.phone || '').includes(search) || (l.email || '').toLowerCase().includes(search);
    return matchSearch && (!status || l.status === status) && (!source || l.source === source);
  });

  renderTable(filtered);
}

function renderTable(leads) {
  const tbody = document.getElementById('leadsTable');
  if (!leads.length) {
    tbody.innerHTML = '<tr><td colspan="8"><div class="empty-state"><div class="empty-icon">👥</div><p>No leads found</p></div></td></tr>';
    return;
  }
  tbody.innerHTML = leads.map(l => `
    <tr class="clickable" onclick="window.location.href='/lead.html?id=${l.id}'">
      <td><strong>${l.first_name} ${l.last_name}</strong></td>
      <td class="text-muted text-sm">${l.phone || l.email || '—'}</td>
      <td>${statusBadge(l.status)}</td>
      <td>${scoreBar(l.score)}</td>
      <td class="text-muted text-sm" style="text-transform:capitalize">${l.source}</td>
      <td class="text-sm">${fmtMoney(l.coverage_amount)}</td>
      <td class="text-muted text-sm">${fmtDate(l.created_at)}</td>
      <td><button class="btn btn-outline btn-sm" onclick="event.stopPropagation();confirmDelete(${l.id},'${l.first_name} ${l.last_name}')">Delete</button></td>
    </tr>
  `).join('');
}

function openAddModal() {
  document.getElementById('addModal').classList.add('show');
  document.getElementById('aFirstName').focus();
}

function closeModal() {
  document.getElementById('addModal').classList.remove('show');
  ['aFirstName','aLastName','aPhone','aEmail','aAge','aIncome','aCoverage','aNotes'].forEach(id => document.getElementById(id).value = '');
  document.getElementById('aHealth').value = '';
  document.getElementById('aSource').value = 'manual';
  document.getElementById('aStatus').value = 'new';
}

async function submitLead() {
  const firstName = document.getElementById('aFirstName').value.trim();
  const lastName = document.getElementById('aLastName').value.trim();
  if (!firstName || !lastName) { showToast('First and last name are required', 'error'); return; }

  try {
    await api.leads.create({
      first_name: firstName,
      last_name: lastName,
      phone: document.getElementById('aPhone').value.trim() || null,
      email: document.getElementById('aEmail').value.trim() || null,
      age: parseInt(document.getElementById('aAge').value) || null,
      annual_income: parseFloat(document.getElementById('aIncome').value) || null,
      coverage_amount: parseFloat(document.getElementById('aCoverage').value) || null,
      health_status: document.getElementById('aHealth').value || null,
      source: document.getElementById('aSource').value,
      status: document.getElementById('aStatus').value,
      notes: document.getElementById('aNotes').value.trim() || null,
    });
    showToast('Lead added', 'success');
    closeModal();
    loadLeads();
  } catch (e) {
    showToast('Error: ' + e.message, 'error');
  }
}

async function confirmDelete(id, name) {
  if (!confirm(`Delete ${name}? This cannot be undone.`)) return;
  try {
    await api.leads.delete(id);
    showToast('Lead deleted', 'success');
    allLeads = allLeads.filter(l => l.id !== id);
    filterLeads();
  } catch (e) {
    showToast('Error: ' + e.message, 'error');
  }
}

loadLeads();
