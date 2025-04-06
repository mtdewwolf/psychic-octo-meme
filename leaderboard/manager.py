import json
import os
from datetime import datetime

class LeaderboardManager:
    def __init__(self):
        self.scores_file = 'leaderboard/scores.json'
        self._ensure_scores_file()
        
    def _ensure_scores_file(self):
        """Ensure the scores file exists with initial structure"""
        if not os.path.exists('leaderboard'):
            os.makedirs('leaderboard')
            
        if not os.path.exists(self.scores_file):
            initial_data = {
                'tictactoe': [],
                'pong': [],
                'last_updated': str(datetime.now())
            }
            with open(self.scores_file, 'w') as f:
                json.dump(initial_data, f, indent=4)
                
    def update_score(self, game_type, username, score):
        """Update the score for a player in a specific game"""
        with open(self.scores_file, 'r') as f:
            data = json.load(f)
            
        # Find existing entry or create new one
        game_scores = data[game_type]
        player_entry = next((entry for entry in game_scores if entry['username'] == username), None)
        
        if player_entry:
            # Update existing score if new score is higher
            if score > player_entry['score']:
                player_entry['score'] = score
                player_entry['last_updated'] = str(datetime.now())
        else:
            # Add new entry
            game_scores.append({
                'username': username,
                'score': score,
                'last_updated': str(datetime.now())
            })
            
        # Sort scores in descending order
        data[game_type] = sorted(game_scores, key=lambda x: x['score'], reverse=True)
        data['last_updated'] = str(datetime.now())
        
        # Write back to file
        with open(self.scores_file, 'w') as f:
            json.dump(data, f, indent=4)
            
    def get_leaderboard(self, game_type, limit=10):
        """Get the top scores for a specific game"""
        with open(self.scores_file, 'r') as f:
            data = json.load(f)
            
        return data[game_type][:limit]
        
    def get_player_rank(self, game_type, username):
        """Get a player's rank in a specific game"""
        with open(self.scores_file, 'r') as f:
            data = json.load(f)
            
        game_scores = data[game_type]
        for i, entry in enumerate(game_scores, 1):
            if entry['username'] == username:
                return i
        return None 