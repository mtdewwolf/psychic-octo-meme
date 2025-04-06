// Initialize Socket.IO connection
const socket = io();

// Game state management
let currentGame = null;
let gameState = null;
let isPlayerTurn = false;

// Socket event handlers
socket.on('connect', () => {
    console.log('Connected to server');
});

socket.on('game_update', (data) => {
    updateGameState(data);
});

socket.on('error', (data) => {
    showError(data.msg);
});

socket.on('status', (data) => {
    updateStatus(data.msg);
});

// Game management functions
function joinGame(gameType, roomId) {
    socket.emit('join', {
        room: roomId,
        gameType: gameType
    });
    currentGame = gameType;
}

function leaveGame(roomId) {
    socket.emit('leave', {
        room: roomId
    });
    currentGame = null;
    gameState = null;
}

function makeMove(moveData) {
    if (!isPlayerTurn) {
        showError("It's not your turn!");
        return;
    }
    
    socket.emit('game_move', {
        room: currentGame,
        move: moveData,
        timestamp: Date.now()
    });
}

function updateGameState(data) {
    gameState = data;
    isPlayerTurn = data.isPlayerTurn;
    renderGame();
}

function renderGame() {
    if (!gameState) return;
    
    switch (currentGame) {
        case 'tictactoe':
            renderTicTacToe();
            break;
        case 'pong':
            renderPong();
            break;
    }
}

// TicTacToe specific functions
function renderTicTacToe() {
    const board = document.querySelector('.game-board');
    if (!board) return;
    
    board.innerHTML = '';
    gameState.board.forEach((cell, index) => {
        const cellElement = document.createElement('div');
        cellElement.className = 'game-cell';
        cellElement.textContent = cell;
        cellElement.addEventListener('click', () => makeMove({ position: index }));
        board.appendChild(cellElement);
    });
}

// Pong specific functions
function renderPong() {
    const container = document.querySelector('.pong-container');
    if (!container) return;
    
    // Update paddle positions
    const leftPaddle = document.querySelector('.left-paddle');
    const rightPaddle = document.querySelector('.right-paddle');
    const ball = document.querySelector('.ball');
    
    if (leftPaddle) leftPaddle.style.top = `${gameState.leftPaddle}px`;
    if (rightPaddle) rightPaddle.style.top = `${gameState.rightPaddle}px`;
    if (ball) {
        ball.style.left = `${gameState.ballX}px`;
        ball.style.top = `${gameState.ballY}px`;
    }
}

// UI helper functions
function showError(message) {
    // Implement error display logic
    console.error(message);
}

function updateStatus(message) {
    // Implement status update logic
    console.log(message);
}

// Event listeners for game controls
document.addEventListener('keydown', (e) => {
    if (currentGame === 'pong' && isPlayerTurn) {
        switch (e.key) {
            case 'ArrowUp':
                makeMove({ direction: 'up' });
                break;
            case 'ArrowDown':
                makeMove({ direction: 'down' });
                break;
        }
    }
}); 