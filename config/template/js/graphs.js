/* ============================================================
   graphs.js
   Builds every Chart.js chart from the REPORT bootstrap object,
   renders their tables, and toggles graph/table views.
   Reads ONLY from window.REPORT — no template syntax here.
   ============================================================ */

/* module-scope handles so renderChartTable / resize can reach them */
let summaryChartInstance, timeChartInstance, sectionChartInstance, trendChartInstance;

/* ---------- DONUT ---------- */
(function(){
    const ctx = document.getElementById('overviewPie');
    if(!ctx) return;
    new Chart(ctx, {
        type:'doughnut',
        data:{ labels:['Passed','Failed'],
               datasets:[{ data:[REPORT.passed, REPORT.failed], backgroundColor:['#22c55e','#ef4444'], borderWidth:0 }] },
        options:{ cutout:'70%', responsive:true, maintainAspectRatio:false, plugins:{ legend:{ display:false } } }
    });
})();

/* ---------- SUMMARY BAR ---------- */
(function(){
    const ctx = document.getElementById('summaryChart');
    if(!ctx) return;
    summaryChartInstance = new Chart(ctx,{
        type:'bar',
        data:{ labels:['Passed','Failed'],
               datasets:[{ data:[REPORT.passed, REPORT.failed], backgroundColor:['#22c55e','#ef4444'], borderRadius:6, barThickness:30 }] },
        options:{ indexAxis:'y', responsive:true, maintainAspectRatio:false,
            plugins:{ legend:{ display:false } },
            scales:{ x:{ beginAtZero:true, ticks:{color:'#9ca3af'}, grid:{color:'rgba(255,255,255,0.05)'} },
                     y:{ ticks:{color:'#f9fafb'}, grid:{display:false} } } }
    });
})();

/* ---------- SECTION-WISE BAR ---------- */
(function(){
    const ctx = document.getElementById('sectionChart');
    if(!ctx) return;
    sectionChartInstance = new Chart(ctx,{
        type:'bar',
        data:{ labels:REPORT.sectionLabels,
               datasets:[ { label:'Passed', data:REPORT.sectionPass, backgroundColor:'#22c55e' },
                          { label:'Failed', data:REPORT.sectionFail, backgroundColor:'#ef4444' } ] },
        options:{ responsive:true, maintainAspectRatio:false, plugins:{ legend:{ display:false } },
            scales:{ x:{ ticks:{color:'#9ca3af'}, grid:{display:false} },
                     y:{ beginAtZero:true, ticks:{color:'#9ca3af'}, grid:{color:'rgba(255,255,255,0.05)'} } } }
    });
})();

/* ---------- EXECUTION TIME (placeholder; values shown as-is) ---------- */
(function(){
    const ctx = document.getElementById('timeChart');
    if(!ctx) return;
    timeChartInstance = new Chart(ctx,{
        type:'line',
        data:{ datasets:[{ data:[{x:0,y:5},{x:20,y:8},{x:40,y:6},{x:60,y:10},{x:80,y:9}],
                           borderColor:'#38bdf8', borderWidth:2, tension:0.3, pointRadius:0, fill:false }] },
        options:{ responsive:true, maintainAspectRatio:false, plugins:{ legend:{ display:false } },
            scales:{ x:{ type:'linear', ticks:{ color:'#9ca3af' }, grid:{color:'rgba(255,255,255,0.05)'} },
                     y:{ display:false } } }
    });
})();

/* ---------- TREND (placeholder; empty state) ---------- */
(function(){
    const ctx = document.getElementById('trendChart');
    if(!ctx) return;
    trendChartInstance = new Chart(ctx,{
        type:'line',
        data:{ labels:[], datasets:[{ label:'Exec Time', data:[], borderColor:'#38bdf8', borderWidth:2, tension:0.3, pointRadius:0, fill:false }] },
        options:{ responsive:true, maintainAspectRatio:false, plugins:{ legend:{ display:false } },
            scales:{ x:{ ticks:{color:'#9ca3af'}, grid:{color:'rgba(255,255,255,0.05)'} }, y:{ display:false } } }
    });
    const empty = document.getElementById('trendEmpty');
    if(empty) empty.style.display = 'block';
})();

/* ---------- TABLES ---------- */
renderChartTable('summaryChartTable', summaryChartInstance);
renderChartTable('timeChartTable',    timeChartInstance);
renderChartTable('sectionChartTable', sectionChartInstance);
renderChartTable('trendChartTable',   trendChartInstance);

/* ---------- GRAPH / TABLE VIEW TOGGLE ---------- */
function setGraphView(cardId, viewType){
    const card = document.getElementById(cardId);
    if(!card) return;
    card.querySelector('.graph-view').style.display = viewType==='graph' ? 'block' : 'none';
    card.querySelector('.table-view').style.display = viewType==='table' ? 'block' : 'none';
    card.querySelectorAll('[data-view-btn]').forEach(btn=>{
        btn.classList.toggle('active', btn.dataset.viewBtn===viewType);
    });
}
