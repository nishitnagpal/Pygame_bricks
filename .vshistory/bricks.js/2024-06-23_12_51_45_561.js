const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

const WIDTH = 1000;
const HEIGHT = 600;

const PLAYER_WIDTH = 100;
const PLAYER_HEIGHT = 10;
const PLAYER_VEL = 5;

const BALL_RADIUS = 10;
const BALL_VEL = 5;

const BRICK_ROWS = 5;
const BRICK_COLS = 10;
const BRICK_WIDTH = WIDTH / BRICK_COLS - 2;
const BRICK_HEIGHT = 30;

let ballMoving = false;
let paused = false;
let score = 0;
let pausedTime = 0;
let endMessage = false;
let winMessage = false;
let elapsedTime = 0;
let pauseStartTime = 0;
let gameStarted = false;
let finalTime = 0;

let startTime;
let player;
let ball;
let ballVel;
let bricks;

const angles = [];
for (let angle = 45; angle < 135; angle++) {
    if ((45 <= angle && angle <= 80) || (100 <= angle < 135)) {
        angles.push(angle * Math.PI / 180);
    }
}

function drawRoundedRectWithBorder(ctx, x, y, width, height, borderColor, fillColor, borderRadius, borderWidth) {
    ctx.fillStyle = borderColor;
    ctx.beginPath();
    ctx.moveTo(x + borderRadius, y);
    ctx.arcTo(x + width, y, x + width, y + height, borderRadius);
    ctx.arcTo(x + width, y + height, x, y + height, borderRadius);
    ctx.arcTo(x, y + height, x, y, borderRadius);
    ctx.arcTo(x, y, x + width, y, borderRadius);
    ctx.closePath();
    ctx.fill();

    ctx.fillStyle = fillColor;
    ctx.beginPath();
    ctx.moveTo(x + borderRadius - borderWidth, y + borderWidth);
    ctx.arcTo(x + width - borderWidth, y + borderWidth, x + width - borderWidth, y + height - borderWidth, borderRadius - borderWidth);
    ctx.arcTo(x + width - borderWidth, y + height - borderWidth, x + borderWidth, y + height - borderWidth, borderRadius - borderWidth);
    ctx.arcTo(x + borderWidth, y + height - borderWidth, x + borderWidth, y + borderWidth, borderRadius - borderWidth);
    ctx.arcTo(x + borderWidth, y + borderWidth, x + width - borderWidth, y + borderWidth, borderRadius - borderWidth);
    ctx.closePath();
    ctx.fill();
}

function draw(player, elapsedTime, ball, bricks, score, showStartMessage, paused, endMessage, finalTime, winMessage) {
    ctx.clearRect(0, 0, WIDTH, HEIGHT);

    if (!endMessage && !winMessage && gameStarted && !paused) {
        ctx.fillStyle = "orange";
        ctx.font = "20px Comic Sans MS";
        ctx.fillText(`Time: ${Math.round(elapsedTime)}s`, 10, 30);
    }

    if (gameStarted) {
        ctx.fillStyle = "orange";
        ctx.font = "20px Comic Sans MS";
        ctx.fillText(`Score: ${score}`, WIDTH - 100, 30);
    }

    ctx.fillStyle = "blue";
    ctx.fillRect(player.x, player.y, player.width, player.height);

    ctx.fillStyle = "yellow";
    ctx.beginPath();
    ctx.arc(ball.x, ball.y, BALL_RADIUS, 0, Math.PI * 2);
    ctx.fill();

    for (const brick of bricks) {
        drawRoundedRectWithBorder(ctx, brick.x, brick.y, brick.width, brick.height, "white", "brown", 10, 3);
    }

    if (showStartMessage && !endMessage && !winMessage) {
        const startText = `Press Enter to Play\n\n Key Bindings \n <- or A : Move left \n -> or D : Move right \n Space : Pause \n q : Quit`;
        drawMultilineText(ctx, startText, "white", WIDTH / 2, HEIGHT / 3);
    }

    if (paused && !showStartMessage) {
        const pauseText = `Game Paused\n\n Press Space to Resume or q to Quit`;
        drawMultilineText(ctx, pauseText, "purple", WIDTH / 2, HEIGHT / 3);
    }

    if (endMessage) {
        const lostText = `You Lost!\nTime Taken: ${Math.round(finalTime)}s\nFinal Score: ${score}\n\nBetter Luck Next Time! \nPress Enter to Play Again or q to Quit`;
        drawMultilineText(ctx, lostText, "red", WIDTH / 2, HEIGHT / 3);
    }

    if (winMessage) {
        const winText = `You Won!\nTime Taken: ${Math.round(finalTime)}s\nFinal Score: ${score}\n\nPress Enter to Play Again or q to Quit`;
        drawMultilineText(ctx, winText, "green", WIDTH / 2, HEIGHT / 3);
    }
}

function drawMultilineText(ctx, text, color, x, y) {
    ctx.fillStyle = color;
    ctx.font = "20px Comic Sans MS";
    const lines = text.split('\n');
    for (let i = 0; i < lines.length; i++) {
        const line = lines[i];
        const metrics = ctx.measureText(line);
        ctx.fillText(line, x - metrics.width / 2, y + i * 30);
    }
}

function resetGame() {
    ballMoving = false;
    paused = false;
    endMessage = false;
    winMessage = false;
    score = 0;
    pausedTime = 0;
    elapsedTime = 0;
    gameStarted = false;
    pauseStartTime = 0;
    finalTime = 0;

    player = { x: (WIDTH - PLAYER_WIDTH) / 2, y: HEIGHT - PLAYER_HEIGHT, width: PLAYER_WIDTH, height: PLAYER_HEIGHT };
    ball = { x: WIDTH / 2, y: HEIGHT - BALL_RADIUS - PLAYER_HEIGHT, radius: BALL_RADIUS };
    ballVel = { x: 0, y: 0 };

    bricks = [];
    for (let row = 0; row < BRICK_ROWS; row++) {
        for (let col = 0; col < BRICK_COLS; col++) {
            bricks.push({ x: col * (BRICK_WIDTH + 2), y: row * BRICK_HEIGHT + 50, width: BRICK_WIDTH, height: BRICK_HEIGHT });
        }
    }
}

function handleBallBrickCollision() {
    for (let i = 0; i < bricks.length; i++) {
        const brick = bricks[i];
        if (ball.x + BALL_RADIUS > brick.x && ball.x - BALL_RADIUS < brick.x + brick.width &&
            ball.y + BALL_RADIUS > brick.y && ball.y - BALL_RADIUS < brick.y + brick.height) {
            bricks.splice(i, 1);
            if (Math.abs(ball.x - (brick.x + brick.width / 2)) > Math.abs(ball.y - (brick.y + brick.height / 2))) {
                ballVel.x = -ballVel.x;
            } else {
                ballVel.y = -ballVel.y;
            }
            return true;
        }
    }
    return false;
}

function main() {
    resetGame();

    function gameLoop() {
        if (gameStarted && !paused) {
            elapsedTime = (Date.now() - startTime - pausedTime) / 1000;
        }

        if (gameStarted && ballMoving && !paused) {
            ball.x += ballVel.x;
            ball.y += ballVel.y;

            if (ball.x - BALL_RADIUS <= 0 || ball.x + BALL_RADIUS >= WIDTH) {
                ballVel.x = -ballVel.x;
            }

            if (ball.y - BALL_RADIUS <= 50) {
                ballVel.y = -ballVel.y;
            }

            if (ball.y + BALL_RADIUS >= HEIGHT) {
                if (ball.x < player.x || ball.x > player.x + player.width) {
                    finalTime = elapsedTime;
                    ballMoving = false;
                    endMessage = true;
                } else {
                    ball.y = player.y - BALL_RADIUS;
                    ballVel.y = -ballVel.y;
                }
            }

            if (ball.y + BALL_RADIUS > player.y && ball.y - BALL_RADIUS < player.y + player.height &&
                ball.x + BALL_RADIUS > player.x && ball.x - BALL_RADIUS < player.x + player.width) {
                ballVel.y = -ballVel.y;
            }

            if (handleBallBrickCollision()) {
                score += 1;
            }

            if (bricks.length === 0) {
                finalTime = elapsedTime;
                ballMoving = false;
                winMessage = true;
            }
        }

        draw(player, elapsedTime, ball, bricks, score, !ballMoving, paused, endMessage, finalTime, winMessage);

        requestAnimationFrame(gameLoop);
    }

    document.addEventListener('keydown', (event) => {
        if (event.key === 'Enter') {
            if (!gameStarted && !endMessage && !winMessage) {
                gameStarted = true;
                startTime = Date.now();
            }

            if (!ballMoving && gameStarted && !endMessage && !winMessage) {
                ballMoving = true;
                const angle = angles[Math.floor(Math.random() * angles.length)];
                ballVel.x = BALL_VEL * Math.cos(angle);
                ballVel.y = BALL_VEL * Math.sin(angle);
            }

            if (endMessage || winMessage) {
                resetGame();
            }
        } else if (event.key === 'q') {
            paused = true;
        } else if (event.key === ' ') {
            paused = !paused;
            if (paused) {
                pauseStartTime = Date.now();
            } else {
                pausedTime += Date.now() - pauseStartTime;
            }
        }
    });

    document.addEventListener('keydown', (event) => {
        if (event.key === 'ArrowLeft' || event.key === 'a') {
            if (player.x - PLAYER_VEL >= 0) {
                player.x -= PLAYER_VEL;
            }
        } else if (event.key === 'ArrowRight' || event.key === 'd') {
            if (player.x + PLAYER_VEL + player.width <= WIDTH) {
                player.x += PLAYER_VEL;
            }
        }
    });

    requestAnimationFrame(gameLoop);
}

main();
