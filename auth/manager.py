import json
import os
import hashlib
import secrets
from datetime import datetime
from typing import Dict, Optional
from werkzeug.security import generate_password_hash, check_password_hash

class AuthManager:
    def __init__(self):
        self.users_file = 'auth/users.json'
        self._ensure_users_file()
        
    def _ensure_users_file(self):
        """Ensure the users file exists with initial structure"""
        if not os.path.exists('auth'):
            os.makedirs('auth')
            
        if not os.path.exists(self.users_file):
            initial_data = {
                'users': [],
                'last_updated': str(datetime.now())
            }
            with open(self.users_file, 'w') as f:
                json.dump(initial_data, f, indent=4)
                
    def register_user(self, username: str, password: str, email: str) -> bool:
        """Register a new user"""
        if self.get_user(username):
            return False
            
        user = {
            'username': username,
            'password_hash': generate_password_hash(password),
            'email': email,
            'created_at': str(datetime.now()),
            'last_login': None,
            'profile': {
                'games_played': 0,
                'games_won': 0,
                'tournaments_joined': 0,
                'tournaments_won': 0,
                'rating': 1000  # Initial rating
            },
            'preferences': {
                'theme': 'light',
                'notifications': True
            }
        }
        
        with open(self.users_file, 'r') as f:
            data = json.load(f)
            
        data['users'].append(user)
        data['last_updated'] = str(datetime.now())
        
        with open(self.users_file, 'w') as f:
            json.dump(data, f, indent=4)
            
        return True
        
    def authenticate_user(self, username: str, password: str) -> bool:
        """Authenticate a user"""
        user = self.get_user(username)
        if not user:
            return False
            
        if check_password_hash(user['password_hash'], password):
            self.update_last_login(username)
            return True
            
        return False
        
    def get_user(self, username: str) -> Optional[Dict]:
        """Get user details"""
        with open(self.users_file, 'r') as f:
            data = json.load(f)
            
        return next((user for user in data['users'] if user['username'] == username), None)
        
    def update_profile(self, username: str, profile_data: Dict) -> bool:
        """Update user profile"""
        with open(self.users_file, 'r') as f:
            data = json.load(f)
            
        user = next((user for user in data['users'] if user['username'] == username), None)
        if not user:
            return False
            
        user['profile'].update(profile_data)
        data['last_updated'] = str(datetime.now())
        
        with open(self.users_file, 'w') as f:
            json.dump(data, f, indent=4)
            
        return True
        
    def update_preferences(self, username: str, preferences: Dict) -> bool:
        """Update user preferences"""
        with open(self.users_file, 'r') as f:
            data = json.load(f)
            
        user = next((user for user in data['users'] if user['username'] == username), None)
        if not user:
            return False
            
        user['preferences'].update(preferences)
        data['last_updated'] = str(datetime.now())
        
        with open(self.users_file, 'w') as f:
            json.dump(data, f, indent=4)
            
        return True
        
    def update_last_login(self, username: str):
        """Update user's last login time"""
        with open(self.users_file, 'r') as f:
            data = json.load(f)
            
        user = next((user for user in data['users'] if user['username'] == username), None)
        if user:
            user['last_login'] = str(datetime.now())
            data['last_updated'] = str(datetime.now())
            
            with open(self.users_file, 'w') as f:
                json.dump(data, f, indent=4)
                
    def update_game_stats(self, username: str, game_won: bool):
        """Update user's game statistics"""
        with open(self.users_file, 'r') as f:
            data = json.load(f)
            
        user = next((user for user in data['users'] if user['username'] == username), None)
        if user:
            user['profile']['games_played'] += 1
            if game_won:
                user['profile']['games_won'] += 1
                # Update rating (simple ELO-like system)
                user['profile']['rating'] += 10
            else:
                user['profile']['rating'] = max(0, user['profile']['rating'] - 5)
                
            data['last_updated'] = str(datetime.now())
            
            with open(self.users_file, 'w') as f:
                json.dump(data, f, indent=4)
                
    def update_tournament_stats(self, username: str, tournament_won: bool):
        """Update user's tournament statistics"""
        with open(self.users_file, 'r') as f:
            data = json.load(f)
            
        user = next((user for user in data['users'] if user['username'] == username), None)
        if user:
            user['profile']['tournaments_joined'] += 1
            if tournament_won:
                user['profile']['tournaments_won'] += 1
                user['profile']['rating'] += 50
            else:
                user['profile']['rating'] = max(0, user['profile']['rating'] - 10)
                
            data['last_updated'] = str(datetime.now())
            
            with open(self.users_file, 'w') as f:
                json.dump(data, f, indent=4) 