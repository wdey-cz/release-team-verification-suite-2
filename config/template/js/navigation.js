/* ============================================================
   navigation.js
   Section switching and sidebar collapse.
   ============================================================ */

function showSection(section, element){
    ['overview','graphs','details','snake','profile'].forEach(id => {
        const el = document.getElementById(id + 'Section');
        if(el) el.style.display = (section === id) ? 'block' : 'none';
    });

    if(section === 'snake')   setTimeout(startSnakeGame, 100);   /* snake.js */
    if(section === 'profile') loadProfileData();                  /* profile.js */

    document.querySelectorAll('.sidebar .nav-item').forEach(el => el.classList.remove('active'));

    if(element && element.classList.contains('nav-item')){
        element.classList.add('active');
    } else {
        /* logo / profile-icon / programmatic call → activate matching menu item */
        const match = document.querySelector('.sidebar .nav-item[data-nav="'+section+'"]')
                   || document.querySelector('.sidebar .nav-menu .nav-item');
        if(match) match.classList.add('active');
    }
}

function toggleSidebar(){
    document.querySelector('.sidebar').classList.toggle('collapsed');
    setTimeout(()=>{ Object.values(Chart.instances).forEach(c=>c.resize()); }, 300);
}
