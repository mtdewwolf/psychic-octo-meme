import json
import os
from datetime import datetime
from typing import List, Dict, Optional

class TournamentManager:
    def __init__(self):
        self.tournaments_file = 'tournament/tournaments.json'
        self._ensure_tournaments_file()
        
    def _ensure_tournaments_file(self):
        """Ensure the tournaments file exists with initial structure"""
        if not os.path.exists('tournament'):
            os.makedirs('tournament')
            
        if not os.path.exists(self.tournaments_file):
            initial_data = {
                'tournaments': [],
                'last_updated': str(datetime.now())
            }
            with open(self.tournaments_file, 'w') as f:
                json.dump(initial_data, f, indent=4)
                
    def create_tournament(self, name: str, game_type: str, max_players: int) -> str:
        """Create a new tournament"""
        tournament_id = f"{game_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        tournament = {
            'id': tournament_id,
            'name': name,
            'game_type': game_type,
            'max_players': max_players,
            'players': [],
            'matches': [],
            'status': 'registration',
            'created_at': str(datetime.now()),
            'started_at': None,
            'ended_at': None,
            'winner': None
        }
        
        with open(self.tournaments_file, 'r') as f:
            data = json.load(f)
            
        data['tournaments'].append(tournament)
        data['last_updated'] = str(datetime.now())
        
        with open(self.tournaments_file, 'w') as f:
            json.dump(data, f, indent=4)
            
        return tournament_id
        
    def register_player(self, tournament_id: str, username: str) -> bool:
        """Register a player for a tournament"""
        with open(self.tournaments_file, 'r') as f:
            data = json.load(f)
            
        tournament = next((t for t in data['tournaments'] if t['id'] == tournament_id), None)
        if not tournament or tournament['status'] != 'registration':
            return False
            
        if username in tournament['players']:
            return False
            
        if len(tournament['players']) >= tournament['max_players']:
            return False
            
        tournament['players'].append(username)
        data['last_updated'] = str(datetime.now())
        
        with open(self.tournaments_file, 'w') as f:
            json.dump(data, f, indent=4)
            
        return True
        
    def start_tournament(self, tournament_id: str) -> bool:
        """Start a tournament and create initial matches"""
        with open(self.tournaments_file, 'r') as f:
            data = json.load(f)
            
        tournament = next((t for t in data['tournaments'] if t['id'] == tournament_id), None)
        if not tournament or tournament['status'] != 'registration':
            return False
            
        if len(tournament['players']) < 2:
            return False
            
        # Create initial matches
        players = tournament['players']
        matches = []
        
        # Simple single-elimination bracket
        while len(players) > 1:
            round_matches = []
            for i in range(0, len(players), 2):
                if i + 1 < len(players):
                    match = {
                        'id': f"{tournament_id}_match_{len(matches)}",
                        'player1': players[i],
                        'player2': players[i + 1],
                        'winner': None,
                        'status': 'pending'
                    }
                    round_matches.append(match)
            matches.extend(round_matches)
            players = [m['player1'] for m in round_matches]  # Temporary, will be updated with winners
            
        tournament['matches'] = matches
        tournament['status'] = 'in_progress'
        tournament['started_at'] = str(datetime.now())
        data['last_updated'] = str(datetime.now())
        
        with open(self.tournaments_file, 'w') as f:
            json.dump(data, f, indent=4)
            
        return True
        
    def record_match_result(self, tournament_id: str, match_id: str, winner: str) -> bool:
        """Record the result of a match"""
        with open(self.tournaments_file, 'r') as f:
            data = json.load(f)
            
        tournament = next((t for t in data['tournaments'] if t['id'] == tournament_id), None)
        if not tournament or tournament['status'] != 'in_progress':
            return False
            
        match = next((m for m in tournament['matches'] if m['id'] == match_id), None)
        if not match or match['status'] != 'pending':
            return False
            
        match['winner'] = winner
        match['status'] = 'completed'
        
        # Check if tournament is complete
        if all(m['status'] == 'completed' for m in tournament['matches']):
            tournament['status'] = 'completed'
            tournament['ended_at'] = str(datetime.now())
            tournament['winner'] = tournament['matches'][-1]['winner']
            
        data['last_updated'] = str(datetime.now())
        
        with open(self.tournaments_file, 'w') as f:
            json.dump(data, f, indent=4)
            
        return True
        
    def get_tournament(self, tournament_id: str) -> Optional[Dict]:
        """Get tournament details"""
        with open(self.tournaments_file, 'r') as f:
            data = json.load(f)
            
        return next((t for t in data['tournaments'] if t['id'] == tournament_id), None)
        
    def get_active_tournaments(self) -> List[Dict]:
        """Get all active tournaments"""
        with open(self.tournaments_file, 'r') as f:
            data = json.load(f)
            
        return [t for t in data['tournaments'] if t['status'] in ['registration', 'in_progress']] 