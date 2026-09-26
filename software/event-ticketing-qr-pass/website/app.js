const $ = (s) => document.querySelector(s);
const adminKey = () => localStorage.getItem('mmk_admin_key') || '';
const headers = (json=true) => { const h = {'X-MMK-Admin-Key': adminKey()}; if(json) h['Content-Type']='application/json'; return h; };

$('#saveKey').addEventListener('click', () => {
  localStorage.setItem('mmk_admin_key', $('#adminKey').value.trim());
  $('#keyStatus').textContent = 'Key saved on this device.';
  loadEvents();
});
$('#adminKey').value = adminKey();

async function api(path, opts={}) {
  const r = await fetch(path, {...opts, headers: {...headers(!!opts.body), ...(opts.headers||{})}});
  let data; try { data = await r.json(); } catch { data = {error: await r.text()}; }
  if (!r.ok) throw new Error(data.error || `Request failed (${r.status})`);
  return data;
}

function eventLabel(e){return `${e.name} — ${e.event_date} ${e.event_time} — ${e.venue}`}
function renderEvents(events){
  $('#eventSelect').innerHTML = events.map(e => `<option value="${e.id}">${escapeHtml(eventLabel(e))}</option>`).join('');
  $('#events').innerHTML = events.length ? events.map(e => `
    <div class="event"><div><strong>${escapeHtml(e.name)}</strong><div class="event-meta">${escapeHtml(e.event_date)} · ${escapeHtml(e.event_time)} · ${escapeHtml(e.venue)} · ${money(e.price_cents)}</div><div class="event-meta">Tickets: ${e.ticket_count} / ${e.capacity || '∞'} · Checked in: ${e.checked_in || 0}</div></div><div class="event-actions"><button class="secondary" data-select="${e.id}">Use event</button><button class="secondary" data-export="${e.id}">Export ZIP</button></div></div>`).join('') : '<p class="muted">No events yet. Create the first event above.</p>';
  document.querySelectorAll('[data-select]').forEach(b => b.addEventListener('click', ()=>{$('#eventSelect').value=b.dataset.select; window.scrollTo({top:document.querySelector('#ticketForm').getBoundingClientRect().top+scrollY-90,behavior:'smooth'}); }));
  document.querySelectorAll('[data-export]').forEach(b => b.addEventListener('click', async ()=>{ try { const r=await fetch(`/api/events/${b.dataset.export}/export.zip`,{headers:headers(false)}); if(!r.ok) throw new Error('Export failed'); const blob=await r.blob(); const url=URL.createObjectURL(blob); const a=document.createElement('a'); a.href=url; a.download='MMK-event-export.zip'; document.body.appendChild(a); a.click(); a.remove(); URL.revokeObjectURL(url); } catch(e){ alert(e.message); } }));
}
async function loadEvents(){ try { renderEvents(await api('/api/events',{headers:{}})); } catch(e){ $('#events').innerHTML=`<p class="muted">${escapeHtml(e.message)}</p>`; }}

$('#eventForm').addEventListener('submit', async (ev)=>{
  ev.preventDefault(); const data=Object.fromEntries(new FormData(ev.target));
  try { await api('/api/events',{method:'POST',body:JSON.stringify(data)}); ev.target.reset(); await loadEvents(); alert('Event created.'); } catch(e){ alert(e.message); }
});

$('#ticketForm').addEventListener('submit', async (ev)=>{
  ev.preventDefault(); const data=Object.fromEntries(new FormData(ev.target));
  if(!data.price) delete data.price;
  data.event_id=Number(data.event_id);
  try {
    const t=await api('/api/tickets',{method:'POST',body:JSON.stringify(data)});
    renderTicket(t);
    await loadEvents();
  } catch(e){ alert(e.message); }
});

$('#bulkIssue').addEventListener('click', async ()=>{
  const event_id=Number($('#eventSelect').value); const csv=$('#bulkCsv').value.trim();
  if(!csv) return alert('Paste CSV rows first.');
  try { const r=await api('/api/tickets/bulk',{method:'POST',body:JSON.stringify({event_id,csv})}); $('#bulkResult').innerHTML=`<div class="ticket-card"><strong>Created:</strong> ${r.created.length} · <strong>Errors:</strong> ${r.errors.length}</div>`; await loadEvents(); } catch(e){alert(e.message);}
});

function renderTicket(t){
  $('#ticketResult').innerHTML=`<div class="ticket-card"><div class="tiny">Ticket generated</div><div class="ticket-code">${escapeHtml(t.code)}</div><div>${escapeHtml(t.attendee_name)} · ${escapeHtml(t.phone)} · ${money(t.price_cents)}</div><div class="event-actions" style="margin-top:10px"><a class="secondary" href="${t.ticket_url}" target="_blank">Open pass</a><a class="secondary" href="${t.pdf_url}" target="_blank">PDF</a><a class="primary" href="${t.whatsapp_url}" target="_blank">WhatsApp</a></div></div>`;
  $('#lastTicket').innerHTML=`<strong>${escapeHtml(t.code)}</strong> · ${escapeHtml(t.attendee_name)} · <a href="${t.ticket_url}" target="_blank">Open QR/check-in pass</a>`;
}
function money(cents){return `R${(Number(cents||0)/100).toFixed(2)}`}
function escapeHtml(v){return String(v??'').replace(/[&<>'"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]));}
$('#refresh').addEventListener('click',loadEvents);
loadEvents();
