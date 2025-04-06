class TicTacToe:
    def __init__(self):
        self.board = [' '] * 9
        self.current_player = 'X'
        self.winner = None
        self.game_over = False
        
    def make_move(self, position):
        """Make a move on the board"""
        if self.game_over or position < 0 or position > 8 or self.board[position] != ' ':
            return False
            
        self.board[position] = self.current_player
        self.check_winner()
        
        if not self.game_over:
            self.current_player = 'O' if self.current_player == 'X' else 'X'
            
        return True
        
    def check_winner(self):
        """Check if there's a winner or if the game is a draw"""
        winning_combinations = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Rows
            [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Columns
            [0, 4, 8], [2, 4, 6]              # Diagonals
        ]
        
        for combo in winning_combinations:
            if (self.board[combo[0]] != ' ' and
                self.board[combo[0]] == self.board[combo[1]] == self.board[combo[2]]):
                self.winner = self.board[combo[0]]
                self.game_over = True
                return
                
        if ' ' not in self.board:
            self.game_over = True
            
    def get_state(self):
        """Get the current game state"""
        return {
            'board': self.board,
            'current_player': self.current_player,
            'winner': self.winner,
            'game_over': self.game_over
        }
        
    def reset(self):
        """Reset the game"""
        self.board = [' '] * 9
        self.current_player = 'X'
        self.winner = None
        self.game_over = False 