import time
import json
from collections import defaultdict
from typing import Dict, List, Optional
import hashlib
import os

class SecurityWatcher:
    def __init__(self):
        self.user_actions = defaultdict(list)
        self.suspicious_patterns = set()
        self.last_move_time = defaultdict(float)
        self.ip_blacklist = set()
        self.user_blacklist = set()
        self._load_blacklists()
        
    def _load_blacklists(self):
        """Load blacklists from file"""
        if not os.path.exists('security'):
            os.makedirs('security')
            
        try:
            with open('security/blacklists.json', 'r') as f:
                data = json.load(f)
                self.ip_blacklist = set(data.get('ip_blacklist', []))
                self.user_blacklist = set(data.get('user_blacklist', []))
        except FileNotFoundError:
            self._save_blacklists()
            
    def _save_blacklists(self):
        """Save blacklists to file"""
        data = {
            'ip_blacklist': list(self.ip_blacklist),
            'user_blacklist': list(self.user_blacklist)
        }
        with open('security/blacklists.json', 'w') as f:
            json.dump(data, f, indent=4)
            
    def check_move(self, move_data: Dict, user_id: str, ip: str) -> bool:
        """Check if a move is valid and not suspicious"""
        # Check blacklists
        if ip in self.ip_blacklist or user_id in self.user_blacklist:
            return False
            
        current_time = time.time()
        
        # Check move timing
        if current_time - self.last_move_time[user_id] < 0.1:  # Less than 100ms between moves
            self.flag_suspicious(user_id, "Rapid moves detected", ip)
            return False
            
        # Check move validity based on game rules
        if not self._validate_move(move_data):
            self.flag_suspicious(user_id, "Invalid move detected", ip)
            return False
            
        # Check for pattern recognition
        if self._detect_suspicious_pattern(user_id, move_data):
            self.flag_suspicious(user_id, "Suspicious pattern detected", ip)
            return False
            
        # Update last move time
        self.last_move_time[user_id] = current_time
        
        # Log the move
        self.user_actions[user_id].append({
            'time': current_time,
            'move': move_data,
            'ip': ip,
            'hash': self._hash_move(move_data)
        })
        
        return True
        
    def _validate_move(self, move_data: Dict) -> bool:
        """Validate the move based on game rules"""
        # Add specific game validation logic here
        # For TicTacToe: check if the move is within bounds and the cell is empty
        # For Pong: check if the paddle movement is within valid range
        return True
        
    def _detect_suspicious_pattern(self, user_id: str, move_data: Dict) -> bool:
        """Detect suspicious patterns in user moves"""
        actions = self.user_actions[user_id]
        if len(actions) < 3:
            return False
            
        # Check for repeated patterns
        recent_moves = [action['hash'] for action in actions[-3:]]
        if len(set(recent_moves)) == 1:  # Same move repeated 3 times
            return True
            
        # Check for impossible move sequences
        # Add more pattern detection logic here
        
        return False
        
    def _hash_move(self, move_data: Dict) -> str:
        """Create a hash of the move data"""
        move_str = json.dumps(move_data, sort_keys=True)
        return hashlib.md5(move_str.encode()).hexdigest()
        
    def flag_suspicious(self, user_id: str, reason: str, ip: str):
        """Flag suspicious behavior"""
        self.suspicious_patterns.add((user_id, reason, ip))
        
        # Log suspicious activity
        with open('security/suspicious_activity.log', 'a') as f:
            f.write(f"{time.time()}: User {user_id} (IP: {ip}) - {reason}\n")
            
        # Add to blacklist after multiple violations
        violations = sum(1 for uid, _, _ in self.suspicious_patterns if uid == user_id)
        if violations >= 3:
            self.user_blacklist.add(user_id)
            self.ip_blacklist.add(ip)
            self._save_blacklists()
            
    def get_user_stats(self, user_id: str) -> Optional[Dict]:
        """Get statistics for a user"""
        actions = self.user_actions[user_id]
        if not actions:
            return None
            
        return {
            'total_moves': len(actions),
            'average_time_between_moves': self._calculate_average_time(actions),
            'suspicious_activity': [reason for uid, reason, _ in self.suspicious_patterns if uid == user_id],
            'is_blacklisted': user_id in self.user_blacklist
        }
        
    def _calculate_average_time(self, actions: List[Dict]) -> float:
        """Calculate average time between moves"""
        if len(actions) < 2:
            return 0
        times = [action['time'] for action in actions]
        intervals = [times[i] - times[i-1] for i in range(1, len(times))]
        return sum(intervals) / len(intervals)
        
    def get_security_report(self) -> Dict:
        """Generate a security report"""
        return {
            'total_suspicious_events': len(self.suspicious_patterns),
            'blacklisted_users': len(self.user_blacklist),
            'blacklisted_ips': len(self.ip_blacklist),
            'recent_suspicious_activity': list(self.suspicious_patterns)[-10:] if self.suspicious_patterns else []
        } 