/* ============================================================
   profile.js
   Profile stats, the motivational stats popup, and confetti.
   Reads counts from window.REPORT.
   ============================================================ */

function loadProfileData(){
    const total = REPORT.total, passed = REPORT.passed, failed = REPORT.failed;
    const rate = total ? Math.round((passed / total) * 100) : 0;

    document.getElementById("profileRuns").innerText  = total;
    document.getElementById("failureCount").innerText = failed;
    document.getElementById("successRate").innerText  = rate + "%";

    let achievement = "🌱 Beginner";
    if(rate >= 95) achievement = "🏆 Automation Overlord";
    else if(rate >= 80) achievement = "🔥 RTVS Power User";
    else if(rate >= 50) achievement = "⚡ Rising Tester";

    document.getElementById("achievementBox").innerText = achievement;
    document.getElementById("activityBox").innerText = `Last run: ${total} test case(s) processed`;
}

function showStats(){
    const total = REPORT.total;
    const msgs = total > 500
        ? ["Do you even sleep or just run RTVS?","HR is concerned. We are too."]
        : ["Great consistency 💪","You're getting sharper 🔥"];
    document.getElementById('popupRuns').innerText = `Test cases run: ${total}`;
    document.getElementById('popupMessage').innerText = msgs[Math.floor(Math.random()*msgs.length)];
    document.getElementById('statPopup').classList.add('show');
    launchConfetti();
    setTimeout(()=>document.getElementById('statPopup').classList.remove('show'), 3000);
}

function launchConfetti(){
    const canvas = document.getElementById('confettiCanvas'), ctx = canvas.getContext('2d');
    canvas.width = window.innerWidth; canvas.height = window.innerHeight;
    const pieces = Array.from({length:120}, ()=>({
        x:Math.random()*canvas.width,
        y:Math.random()*canvas.height - canvas.height,
        size:Math.random()*6 + 4,
        speed:Math.random()*3 + 2,
        color:['#22c55e','#ef4444','#38bdf8','#facc15'][Math.floor(Math.random()*4)],
        angle:Math.random()*360
    }));
    let frame = 0;
    function draw(){
        ctx.clearRect(0,0,canvas.width,canvas.height);
        pieces.forEach(p=>{ p.y+=p.speed; p.x+=Math.sin(p.angle); ctx.fillStyle=p.color; ctx.fillRect(p.x,p.y,p.size,p.size); });
        if(++frame < 120) requestAnimationFrame(draw);
        else ctx.clearRect(0,0,canvas.width,canvas.height);
    }
    draw();
}
