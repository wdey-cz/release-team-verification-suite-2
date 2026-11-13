/* ============================================================
   utils.js
   Shared helpers used by other modules. Loaded first.
   ============================================================ */

/* Render a chart's data into a <table> for the Table view.
   Handles point data ({x,y}) and labelled series. */
function renderChartTable(tableId, chart){
    const table = document.getElementById(tableId);
    if(!table || !chart) return;

    const labels   = chart.data.labels || [];
    const datasets = chart.data.datasets || [];
    if(!datasets.length){ table.innerHTML = '<thead><tr><th>No data</th></tr></thead>'; return; }

    const isPoints = Array.isArray(datasets[0].data) &&
                     datasets[0].data.length &&
                     typeof datasets[0].data[0] === 'object';

    if(isPoints){
        const rows = datasets[0].data
            .map((p,i)=>`<tr><td>${i+1}</td><td>${p.x}</td><td>${p.y}</td></tr>`)
            .join('');
        table.innerHTML = `<thead><tr><th>#</th><th>X</th><th>Y</th></tr></thead><tbody>${rows}</tbody>`;
        return;
    }

    const heads = ['<th>Label</th>']
        .concat(datasets.map(d=>`<th>${d.label || 'Value'}</th>`))
        .join('');
    const max = Math.max(labels.length, ...datasets.map(d=>d.data ? d.data.length : 0));
    let rows = '';
    for(let i=0;i<max;i++){
        const vals = datasets.map(d=>`<td>${d.data?.[i] ?? ''}</td>`).join('');
        rows += `<tr><td>${labels[i] ?? `Row ${i+1}`}</td>${vals}</tr>`;
    }
    table.innerHTML = `<thead><tr>${heads}</tr></thead><tbody>${rows}</tbody>`;
}

/* Download a canvas chart as a PNG file. */
function exportChartPng(canvasId, fileName){
    const c = document.getElementById(canvasId);
    if(!c) return;
    const a = document.createElement('a');
    a.href = c.toDataURL('image/png');
    a.download = fileName;
    a.click();
}
