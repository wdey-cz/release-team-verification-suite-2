/* ============================================================
   sections.js
   Suite accordion + detail panel: show details, prev/next
   navigation, collapse/expand, keyboard nav.
   ============================================================ */

let currentDetailRow = null;

/* ---------- ACCORDION ---------- */
function toggleSection(header){
    const section = header.parentElement;
    const layout  = header.closest('.details-layout');
    const isOpening = !section.classList.contains('open');

    document.querySelectorAll('.section').forEach(s=>{ if(s!==section) s.classList.remove('open'); });
    section.classList.toggle('open');

    if(!isOpening){
        layout.classList.remove('active');
        currentDetailRow = null;
    }

    const panel = layout.querySelector('.details-panel');
    if(panel) panel.querySelectorAll('.case-detail').forEach(e=>e.style.display='none');
}

/* ---------- SHOW A TEST CASE ---------- */
function showDetails(id, el){
    try {
        const layout  = el.closest('.details-layout');
        const panel   = layout.querySelector('.details-panel');
        const content = panel.querySelector('.detail-content');

        layout.classList.add('active');
        currentDetailRow = el;

        layout.querySelectorAll('.pkg').forEach(p=>p.classList.remove('active'));
        el.classList.add('active');

        /* always expand when opening a new case */
        layout.classList.remove('panel-collapsed');
        document.getElementById('detailCollapseBtn').textContent = 'Hide ▸';

        content.querySelectorAll('.case-detail').forEach(e=>e.style.display='none');
        const emptyMsg = content.querySelector('.empty-state');
        if(emptyMsg) emptyMsg.style.display='none';

        const selectedId = 'detail-' + id;
        const selected = content.querySelector('#' + CSS.escape(selectedId));

        if(selected){
            selected.style.display='block';
            content.scrollTop = 0;
        } else {
            console.warn('showDetails: no matching element for id', selectedId);
            /* replace ONLY the body, keep the nav bar intact */
            content.innerHTML =
                '<div class="empty-state" style="position:static;transform:none;padding:20px;color:#94a3b8;">'
                + 'Could not load details for this test case (id: ' + selectedId + ')</div>';
        }

        updateDetailNav();
    } catch(err){
        console.error('showDetails failed:', err);
    }
}

/* ---------- PREV / NEXT WITHIN THE OPEN SUITE ---------- */
function siblingRows(){
    if(!currentDetailRow) return [];
    return Array.from(currentDetailRow.closest('.section-body').querySelectorAll('.pkg'));
}

function detailNav(dir){
    const rows = siblingRows();
    if(!rows.length) return;
    const idx = rows.indexOf(currentDetailRow);
    const target = rows[idx + dir];
    if(target){
        target.click();
        target.scrollIntoView({block:'nearest'});
    }
}

function updateDetailNav(){
    const rows  = siblingRows();
    const label = document.getElementById('detailNavLabel');
    const prev  = document.getElementById('detailPrevBtn');
    const next  = document.getElementById('detailNextBtn');
    if(!rows.length){ label.textContent = 'Test — of —'; prev.disabled = next.disabled = true; return; }
    const idx = rows.indexOf(currentDetailRow);
    label.textContent = `Test ${idx+1} of ${rows.length}`;
    prev.disabled = (idx <= 0);
    next.disabled = (idx >= rows.length - 1);
}

/* ---------- COLLAPSE / EXPAND ---------- */
function toggleDetailPanel(){
    const layout = document.querySelector('.details-layout');
    const btn = document.getElementById('detailCollapseBtn');
    const collapsed = layout.classList.toggle('panel-collapsed');
    btn.textContent = collapsed ? '‹' : 'Collapse ▸';
}
/* ---------- KEYBOARD NAV (Sections page only) ---------- */
document.addEventListener('keydown', e=>{
    if(document.getElementById('detailsSection').style.display !== 'block') return;
    if(!currentDetailRow) return;
    if(e.key === 'ArrowDown'){ e.preventDefault(); detailNav(1); }
    else if(e.key === 'ArrowUp'){ e.preventDefault(); detailNav(-1); }
});
