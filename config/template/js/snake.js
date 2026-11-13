/* ============================================================
   snake.js
   Canvas snake game. Uses a single named keydown handler that
   is removed before re-adding, so restarts never stack listeners.
   ============================================================ */

let gameStarted=false, gameInterval, timeInterval, score=0, seconds=0;
let snake, direction, food;
const BOX = 20;

function snakeControl(e){
    if(document.getElementById('snakeSection').style.display!=='block') return;
    if(e.key==='ArrowUp'    && direction!=='DOWN')  direction='UP';
    else if(e.key==='ArrowDown'  && direction!=='UP')   direction='DOWN';
    else if(e.key==='ArrowLeft'  && direction!=='RIGHT') direction='LEFT';
    else if(e.key==='ArrowRight' && direction!=='LEFT')  direction='RIGHT';
}

function randomFood(){
    return { x:Math.floor(Math.random()*(1260/BOX))*BOX, y:Math.floor(Math.random()*(720/BOX))*BOX };
}

function startSnakeGame(){
    if(gameStarted) return;
    const canvas = document.getElementById('snakeGameFull');
    const ctx    = canvas.getContext('2d');
    snake=[{x:600,y:360}]; direction='RIGHT'; food=randomFood();
    score=0; seconds=0; updateHUD();

    timeInterval = setInterval(()=>{ seconds++; document.getElementById('time').innerText=seconds; }, 1000);

    document.removeEventListener('keydown', snakeControl);
    document.addEventListener('keydown', snakeControl);

    function draw(){
        ctx.fillStyle='black'; ctx.fillRect(0,0,1260,720);
        snake.forEach((s,i)=>{ ctx.fillStyle=i===0?'#22c55e':'#16a34a'; ctx.fillRect(s.x,s.y,BOX,BOX); });
        ctx.fillStyle='#ef4444'; ctx.fillRect(food.x,food.y,BOX,BOX);

        let head={x:snake[0].x,y:snake[0].y};
        if(direction==='UP')    head.y-=BOX;
        if(direction==='DOWN')  head.y+=BOX;
        if(direction==='LEFT')  head.x-=BOX;
        if(direction==='RIGHT') head.x+=BOX;

        if(head.x===food.x && head.y===food.y){ score++; updateHUD(); food=randomFood(); }
        else { snake.pop(); }

        if(head.x<0||head.y<0||head.x>=1260||head.y>=720||snake.some(s=>s.x===head.x&&s.y===head.y)){ gameOver(); return; }
        snake.unshift(head);
    }
    gameInterval = setInterval(draw, 180);
    gameStarted  = true;
}

function updateHUD(){ document.getElementById('score').innerText = score; }

function restartGame(){
    clearInterval(gameInterval);
    clearInterval(timeInterval);
    gameStarted=false;
    startSnakeGame();
}

function gameOver(){
    clearInterval(gameInterval); clearInterval(timeInterval);
    const canvas=document.getElementById('snakeGameFull'), ctx=canvas.getContext('2d');
    ctx.fillStyle='rgba(0,0,0,0.8)'; ctx.fillRect(0,0,1260,720);
    ctx.fillStyle='white'; ctx.font='40px Segoe UI'; ctx.textAlign='center';
    ctx.fillText('Game Over 😢',630,300); ctx.fillText('Score: '+score,630,360);
    ctx.font='24px Segoe UI';
    ctx.fillText("Press Restart to play again",630,430);
    gameStarted=false;
    document.removeEventListener('keydown', snakeControl);
}
