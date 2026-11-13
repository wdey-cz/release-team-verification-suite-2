/* ============================================================
   app.js
   Entry point. Loaded last. Wires page-load behavior:
   avatar restore, default section, and file:// link blocking.
   ============================================================ */

/* ---------- AVATAR PERSISTENCE (load only) ---------- */
window.addEventListener('load', ()=>{
    const saved = localStorage.getItem('selectedAvatar');
    const img = document.getElementById('profileAvatar');
    const svg = document.getElementById('defaultIcon');
    if(saved){ img.src = saved; img.style.display='block'; svg.style.display='none'; }
    else { img.style.display='none'; svg.style.display='block'; }
});

/* ---------- DEFAULT SECTION ON LOAD ---------- */
window.addEventListener('DOMContentLoaded', ()=>{
    const nav = document.querySelector('[data-nav="overview"]');
    if(nav) showSection('overview', nav);
});

/* ---------- BLOCK file:// LINKS ---------- */
document.addEventListener('click', e=>{
    const link = e.target.closest('a');
    if(!link) return;
    if((link.getAttribute('href') || '').startsWith('file://')) e.preventDefault();
});
