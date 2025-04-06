import random
import math

class Pong:
    def __init__(self, width=800, height=400):
        self.width = width
        self.height = height
        self.paddle_height = 100
        self.paddle_width = 20
        self.ball_size = 20
        self.paddle_speed = 5
        self.ball_speed = 5
        
        # Initialize game state
        self.reset()
        
    def reset(self):
        """Reset the game state"""
        self.left_paddle = self.height // 2 - self.paddle_height // 2
        self.right_paddle = self.height // 2 - self.paddle_height // 2
        self.ball_x = self.width // 2
        self.ball_y = self.height // 2
        self.ball_dx = random.choice([-1, 1]) * self.ball_speed
        self.ball_dy = random.choice([-1, 1]) * self.ball_speed
        self.left_score = 0
        self.right_score = 0
        self.game_over = False
        
    def move_paddle(self, player, direction):
        """Move a paddle up or down"""
        if player == 'left':
            if direction == 'up':
                self.left_paddle = max(0, self.left_paddle - self.paddle_speed)
            else:
                self.left_paddle = min(self.height - self.paddle_height, 
                                     self.left_paddle + self.paddle_speed)
        else:
            if direction == 'up':
                self.right_paddle = max(0, self.right_paddle - self.paddle_speed)
            else:
                self.right_paddle = min(self.height - self.paddle_height, 
                                      self.right_paddle + self.paddle_speed)
                                      
    def update(self):
        """Update the game state"""
        if self.game_over:
            return
            
        # Move ball
        self.ball_x += self.ball_dx
        self.ball_y += self.ball_dy
        
        # Ball collision with top and bottom
        if self.ball_y <= 0 or self.ball_y >= self.height - self.ball_size:
            self.ball_dy *= -1
            
        # Ball collision with paddles
        if (self.ball_x <= self.paddle_width and
            self.left_paddle <= self.ball_y <= self.left_paddle + self.paddle_height):
            self.ball_dx *= -1
            # Add some randomness to the bounce
            self.ball_dy += random.uniform(-1, 1)
            
        if (self.ball_x >= self.width - self.paddle_width - self.ball_size and
            self.right_paddle <= self.ball_y <= self.right_paddle + self.paddle_height):
            self.ball_dx *= -1
            # Add some randomness to the bounce
            self.ball_dy += random.uniform(-1, 1)
            
        # Score points
        if self.ball_x <= 0:
            self.right_score += 1
            self.reset_ball()
        elif self.ball_x >= self.width - self.ball_size:
            self.left_score += 1
            self.reset_ball()
            
        # Check for game over
        if self.left_score >= 5 or self.right_score >= 5:
            self.game_over = True
            
    def reset_ball(self):
        """Reset the ball position"""
        self.ball_x = self.width // 2
        self.ball_y = self.height // 2
        self.ball_dx = random.choice([-1, 1]) * self.ball_speed
        self.ball_dy = random.choice([-1, 1]) * self.ball_speed
        
    def get_state(self):
        """Get the current game state"""
        return {
            'left_paddle': self.left_paddle,
            'right_paddle': self.right_paddle,
            'ball_x': self.ball_x,
            'ball_y': self.ball_y,
            'left_score': self.left_score,
            'right_score': self.right_score,
            'game_over': self.game_over,
            'winner': 'left' if self.left_score >= 5 else 'right' if self.right_score >= 5 else None
        } 