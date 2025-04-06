from flask import Flask, render_template, session, request, jsonify, redirect, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import json
import os
from datetime import datetime
from security.watcher import SecurityWatcher
from auth.manager import AuthManager
from tournament.manager import TournamentManager
from games.tictactoe import TicTacToe
from games.pong import Pong
from leaderboard.manager import LeaderboardManager

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-please-change')
socketio = SocketIO(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Initialize managers
security_watcher = SecurityWatcher()
auth_manager = AuthManager()
tournament_manager = TournamentManager()
leaderboard_manager = LeaderboardManager()

# Active games
active_games = {}

# User class for authentication
class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if auth_manager.authenticate_user(username, password):
            user = User(username)
            login_user(user)
            return redirect(url_for('index'))
        return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        
        if auth_manager.register_user(username, password, email):
            return redirect(url_for('login'))
        return render_template('register.html', error='Username already exists')
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/profile')
@login_required
def profile():
    user_data = auth_manager.get_user(current_user.id)
    return render_template('profile.html', user=user_data)

@app.route('/tournaments')
def tournaments():
    active_tournaments = tournament_manager.get_active_tournaments()
    return render_template('tournaments.html', tournaments=active_tournaments)

@app.route('/tournament/<tournament_id>')
@login_required
def tournament(tournament_id):
    tournament_data = tournament_manager.get_tournament(tournament_id)
    if not tournament_data:
        return redirect(url_for('tournaments'))
    return render_template('tournament.html', tournament=tournament_data)

@app.route('/game/<game_type>')
@login_required
def game(game_type):
    if game_type not in ['tictactoe', 'pong']:
        return redirect(url_for('index'))
    return render_template(f'game_{game_type}.html')

@app.route('/leaderboard')
def leaderboard():
    tictactoe_scores = leaderboard_manager.get_leaderboard('tictactoe')
    pong_scores = leaderboard_manager.get_leaderboard('pong')
    return render_template('leaderboard.html', 
                         tictactoe_scores=tictactoe_scores,
                         pong_scores=pong_scores)

@socketio.on('join')
def on_join(data):
    room = data['room']
    join_room(room)
    emit('status', {'msg': f'{current_user.id} has entered the room.'}, room=room)

@socketio.on('leave')
def on_leave(data):
    room = data['room']
    leave_room(room)
    emit('status', {'msg': f'{current_user.id} has left the room.'}, room=room)

@socketio.on('game_move')
def handle_game_move(data):
    # Security check
    if not security_watcher.check_move(data, current_user.id, request.remote_addr):
        emit('error', {'msg': 'Invalid move detected'})
        return
        
    room = data['room']
    game_type = data['game_type']
    
    # Get or create game instance
    if room not in active_games:
        if game_type == 'tictactoe':
            active_games[room] = TicTacToe()
        elif game_type == 'pong':
            active_games[room] = Pong()
            
    game = active_games[room]
    
    # Handle move based on game type
    if game_type == 'tictactoe':
        if game.make_move(data['position']):
            game_state = game.get_state()
            emit('game_update', game_state, room=room)
            
            if game_state['game_over']:
                # Update leaderboard
                if game_state['winner']:
                    winner = 'X' if game_state['winner'] == 'X' else 'O'
                    leaderboard_manager.update_score('tictactoe', current_user.id, 1)
                    auth_manager.update_game_stats(current_user.id, True)
                else:
                    auth_manager.update_game_stats(current_user.id, False)
                    
    elif game_type == 'pong':
        game.move_paddle(data['player'], data['direction'])
        game.update()
        game_state = game.get_state()
        emit('game_update', game_state, room=room)
        
        if game_state['game_over']:
            winner = game_state['winner']
            if winner:
                leaderboard_manager.update_score('pong', current_user.id, 1)
                auth_manager.update_game_stats(current_user.id, True)
            else:
                auth_manager.update_game_stats(current_user.id, False)

if __name__ == '__main__':
    socketio.run(app, debug=True) 