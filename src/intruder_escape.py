"""
Intruder Escape Game
--------------------
An AI pursuit–evasion game where robots use A* pathfinding to chase the player.
Built with Python and Pygame.
"""

import pygame
import random
import heapq
from typing import Tuple, List, Dict, Optional
import sys
import json
import os

class GridMaze:
    def __init__(self):
        pygame.init()
        
        # Constants
        self.GRID_SIZE = 15
        self.CELL_SIZE = 40
        self.NUM_ROBOTS = 4
        self.NUM_OBSTACLES = 30
        self.ROBOT_SPEED_INITIAL = 1.0
        self.ROBOT_SPEED_INCREASE = 0.1
        self.ROBOT_SPEED_INCREASE_STEPS = 100
        
        # Window setup
        self.PADDING = 20
        self.BUTTON_HEIGHT = 40
        self.BUTTON_WIDTH = 120
        self.BUTTON_SPACING = 10
        self.WINDOW_WIDTH = self.GRID_SIZE * self.CELL_SIZE + 2 * self.PADDING + 160  # Added width for leaderboard
        self.WINDOW_HEIGHT = self.GRID_SIZE * self.CELL_SIZE + 3 * self.BUTTON_HEIGHT + 3 * self.PADDING
        self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        pygame.display.set_caption("Intruder Escape")
        
        # Colors
        self.COLORS = {
            'white': (255, 255, 255),
            'black': (40, 40, 40),
            'gray': (200, 200, 200),
            'light_gray': (240, 240, 240),
            'button_bg': (240, 240, 240),
            'button_hover': (220, 220, 220),
            'red': (255, 0, 0),
            'blue': (0, 122, 255),
            'green': (0, 155, 0),
            'orange': (255, 149, 0),
            'purple': (175, 82, 222),
            'cyan': (52, 199, 235)
        }
        
        # Game state
        self.game_status = "setup"
        self.game_running = False
        self.steps = 0
        self.high_score = self.load_high_score()
        self.robot_speed = self.ROBOT_SPEED_INITIAL
        self.robot_counter = 1
        self.last_update = pygame.time.get_ticks()
        
        # Grid state
        self.grid = [[0 for _ in range(self.GRID_SIZE)] for _ in range(self.GRID_SIZE)]
        self.robots: Dict[Tuple[int, int], int] = {}
        self.intruder_pos = None
        
        # Font setup
        self.font = pygame.font.SysFont('Arial', 16)
        self.button_font = pygame.font.SysFont('Arial', 14, bold=True)
        
        # Initialize game
        self.new_random_layout()

        # Buttons
        self.buttons = [
            {"text": "Clear Grid", "action": self.clear_grid},
            {"text": "Place Intruder", "action": self.add_intruder_mode},
            {"text": "Start Game", "action": self.start_game},
            {"text": "New Layout", "action": self.new_random_layout}
        ]

        # Leaderboard
        self.leaderboard = self.load_leaderboard()

    def load_high_score(self):
        try:
            if os.path.exists('high_score.json'):
                with open('high_score.json', 'r') as f:
                    return json.load(f)['high_score']
        except:
            pass
        return 0

    def save_high_score(self):
        try:
            with open('high_score.json', 'w') as f:
                json.dump({'high_score': self.high_score}, f)
        except:
            pass

    def update_high_score(self):
        if self.steps > self.high_score:
            self.high_score = self.steps
            self.save_high_score()

    def load_leaderboard(self):
        try:
            if os.path.exists('leaderboard.json'):
                with open('leaderboard.json', 'r') as f:
                    return json.load(f)['scores']
        except:
            pass
        return []

    def save_leaderboard(self, scores):
        try:
            with open('leaderboard.json', 'w') as f:
                json.dump({'scores': scores}, f)
        except:
            pass

    def update_leaderboard(self):
        scores = self.load_leaderboard()
        scores.append(self.steps)
        scores.sort(reverse=True)
        scores = scores[:5]  # Keep only top 5 scores
        self.save_leaderboard(scores)
        return scores

    def add_intruder_mode(self):
        if not self.game_running:
            self.game_status = "setup"

    def start_game(self):
        if not self.intruder_pos:
            return
        self.game_status = "running"
        self.game_running = True
        self.robot_speed = self.ROBOT_SPEED_INITIAL
        self.steps = 0

    def new_random_layout(self):
        self.clear_grid()
        self.add_random_obstacles()
        self.add_random_robots()

    def add_random_obstacles(self):
        self.grid = [[0 for _ in range(self.GRID_SIZE)] for _ in range(self.GRID_SIZE)]
        for _ in range(self.NUM_OBSTACLES):
            while True:
                row = random.randint(0, self.GRID_SIZE-1)
                col = random.randint(0, self.GRID_SIZE-1)
                if self.grid[row][col] == 0:
                    self.grid[row][col] = 1
                    break

    def add_random_robots(self):
        self.robots.clear()
        self.robot_counter = 1
        for _ in range(self.NUM_ROBOTS):
            while True:
                row = random.randint(0, self.GRID_SIZE-1)
                col = random.randint(0, self.GRID_SIZE-1)
                if self.grid[row][col] == 0 and (row, col) not in self.robots:
                    self.robots[(row, col)] = self.robot_counter
                    self.robot_counter += 1
                    break

    def clear_grid(self):
        self.grid = [[0 for _ in range(self.GRID_SIZE)] for _ in range(self.GRID_SIZE)]
        self.robots.clear()
        self.robot_counter = 1
        self.intruder_pos = None
        self.game_running = False
        self.game_status = "setup"
        self.steps = 0
        self.robot_speed = self.ROBOT_SPEED_INITIAL

    def find_path(self, start: Tuple[int, int], goal: Tuple[int, int]) -> Optional[List[Tuple[int, int]]]:
        def manhattan_distance(a: Tuple[int, int], b: Tuple[int, int]) -> int:
            return abs(a[0] - b[0]) + abs(a[1] - b[1])
        
        open_set = []
        closed_set = set()
        g_score = {start: 0}
        f_score = {start: manhattan_distance(start, goal)}
        came_from = {}
        
        heapq.heappush(open_set, (f_score[start], start))
        
        while open_set:
            current = heapq.heappop(open_set)[1]
            
            if current == goal:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(start)
                path.reverse()
                return path
            
            closed_set.add(current)
            
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                neighbor = (current[0] + dx, current[1] + dy)
                
                if (not (0 <= neighbor[0] < self.GRID_SIZE and 
                        0 <= neighbor[1] < self.GRID_SIZE) or
                    self.grid[neighbor[0]][neighbor[1]] == 1):
                    continue
                
                if neighbor in closed_set:
                    continue
                
                tentative_g_score = g_score[current] + 1
                
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = g_score[neighbor] + manhattan_distance(neighbor, goal)
                    
                    if neighbor not in [item[1] for item in open_set]:
                        heapq.heappush(open_set, (f_score[neighbor], neighbor))
        
        return None

    def update_game(self):
        if not self.game_running:
            return
            
        current_time = pygame.time.get_ticks()
        if current_time - self.last_update >= 1000 / self.robot_speed:
            new_robots = {}
            for (robot_row, robot_col), number in self.robots.items():
                path = self.find_path((robot_row, robot_col), self.intruder_pos)
                
                if path and len(path) > 1:
                    next_pos = path[1]
                    new_robots[next_pos] = number
                    
                    if next_pos == self.intruder_pos:
                        self.game_over()
                        return
                else:
                    new_robots[(robot_row, robot_col)] = number
            
            self.robots = new_robots
            self.last_update = current_time

    def game_over(self):
        self.game_running = False
        self.game_status = "gameover"
        self.update_high_score()
        self.leaderboard = self.update_leaderboard()

    def draw(self):
        self.screen.fill(self.COLORS['white'])
        
        # Draw buttons
        button_y = self.PADDING
        total_button_width = len(self.buttons) * (self.BUTTON_WIDTH + self.BUTTON_SPACING) - self.BUTTON_SPACING
        start_x = (self.WINDOW_WIDTH - total_button_width) // 2
        
        for i, button in enumerate(self.buttons):
            button_x = start_x + i * (self.BUTTON_WIDTH + self.BUTTON_SPACING)
            button_rect = pygame.Rect(button_x, button_y, self.BUTTON_WIDTH, self.BUTTON_HEIGHT)
            
            # Check hover state
            mouse_pos = pygame.mouse.get_pos()
            if button_rect.collidepoint(mouse_pos):
                color = self.COLORS['button_hover']
            else:
                color = self.COLORS['button_bg']
            
            # Draw button
            pygame.draw.rect(self.screen, color, button_rect)
            pygame.draw.rect(self.screen, self.COLORS['black'], button_rect, 1)
            
            # Draw button text
            text = self.button_font.render(button["text"], True, self.COLORS['black'])
            text_rect = text.get_rect(center=button_rect.center)
            self.screen.blit(text, text_rect)
        
        # Draw grid background
        grid_rect = pygame.Rect(
            self.PADDING,
            2 * self.PADDING + self.BUTTON_HEIGHT,
            self.GRID_SIZE * self.CELL_SIZE,
            self.GRID_SIZE * self.CELL_SIZE
        )
        pygame.draw.rect(self.screen, self.COLORS['light_gray'], grid_rect)
        
        # Draw grid and obstacles
        for row in range(self.GRID_SIZE):
            for col in range(self.GRID_SIZE):
                x = col * self.CELL_SIZE + self.PADDING
                y = row * self.CELL_SIZE + 2 * self.PADDING + self.BUTTON_HEIGHT
                
                # Draw cell
                pygame.draw.rect(self.screen, self.COLORS['black'], 
                               (x, y, self.CELL_SIZE, self.CELL_SIZE), 1)
                
                if self.grid[row][col] == 1:
                    pygame.draw.rect(self.screen, self.COLORS['gray'],
                                   (x + 1, y + 1, self.CELL_SIZE - 2, self.CELL_SIZE - 2))
        
        # Draw robots
        robot_colors = ['blue', 'green', 'orange', 'purple', 'cyan']
        for pos, number in self.robots.items():
            row, col = pos
            x = col * self.CELL_SIZE + self.PADDING + self.CELL_SIZE // 2
            y = row * self.CELL_SIZE + 2 * self.PADDING + self.BUTTON_HEIGHT + self.CELL_SIZE // 2
            color = robot_colors[(number - 1) % len(robot_colors)]
            
            pygame.draw.circle(self.screen, self.COLORS[color],
                             (x, y), self.CELL_SIZE // 3)
            text = self.font.render(str(number), True, self.COLORS['white'])
            text_rect = text.get_rect(center=(x, y))
            self.screen.blit(text, text_rect)
        
        # Draw intruder
        if self.intruder_pos:
            row, col = self.intruder_pos
            x = col * self.CELL_SIZE + self.PADDING + self.CELL_SIZE // 2
            y = row * self.CELL_SIZE + 2 * self.PADDING + self.BUTTON_HEIGHT + self.CELL_SIZE // 2
            pygame.draw.circle(self.screen, self.COLORS['red'],
                             (x, y), self.CELL_SIZE // 3)
            text = self.font.render('I', True, self.COLORS['white'])
            text_rect = text.get_rect(center=(x, y))
            self.screen.blit(text, text_rect)
        
        # Draw leaderboard
        leaderboard_x = self.WINDOW_WIDTH - 150
        leaderboard_y = 100
        
        # Draw leaderboard background
        pygame.draw.rect(self.screen, self.COLORS['light_gray'],
                        (leaderboard_x - 10, leaderboard_y - 30, 140, 160))
        pygame.draw.rect(self.screen, self.COLORS['black'],
                        (leaderboard_x - 10, leaderboard_y - 30, 140, 160), 1)
        
        # Draw leaderboard title
        title_text = self.font.render("Leaderboard", True, self.COLORS['black'])
        title_rect = title_text.get_rect(centerx=leaderboard_x + 60, y=leaderboard_y - 25)
        self.screen.blit(title_text, title_rect)
		
		# Draw scores
        for i, score in enumerate(sorted(self.leaderboard, reverse=True)[:5]):
            text = self.font.render(f"#{i+1}: {score}", True, self.COLORS['black'])
            self.screen.blit(text, (leaderboard_x, leaderboard_y + i * 25))

        # Draw status text
        steps_text = f"Steps: {self.steps}"
        if self.game_running and self.steps > 0:
            steps_until_speed = self.ROBOT_SPEED_INCREASE_STEPS - (self.steps % self.ROBOT_SPEED_INCREASE_STEPS)
            steps_text += f" (Speed increase in: {steps_until_speed})"
        text = self.font.render(steps_text, True, self.COLORS['black'])
        text_rect = text.get_rect(x=self.PADDING, bottom=self.WINDOW_HEIGHT - self.PADDING)
        self.screen.blit(text, text_rect)
        
        # Draw high score
        high_score_text = f"High Score: {self.high_score}"
        text = self.font.render(high_score_text, True, self.COLORS['black'])
        text_rect = text.get_rect(right=self.WINDOW_WIDTH - self.PADDING, bottom=self.WINDOW_HEIGHT - self.PADDING)
        self.screen.blit(text, text_rect)
        
        # Draw status message
        status_text = "Click to place intruder" if self.game_status == "setup" else \
                     "Game Over!" if self.game_status == "gameover" else \
                     "Press SPACE to start" if not self.game_running else \
                     "Use arrow keys to move"
        text = self.font.render(status_text, True, self.COLORS['black'])
        text_rect = text.get_rect(centerx=self.WINDOW_WIDTH // 2, bottom=self.WINDOW_HEIGHT - self.PADDING)
        self.screen.blit(text, text_rect)

        # Draw game over overlay
        if self.game_status == "gameover":
            # Semi-transparent overlay
            overlay = pygame.Surface((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
            overlay.fill(self.COLORS['black'])
            overlay.set_alpha(128)
            self.screen.blit(overlay, (0, 0))
            
            # Game Over text
            game_over_font = pygame.font.SysFont('Arial', 48, bold=True)
            text = game_over_font.render("Game Over!", True, self.COLORS['white'])
            text_rect = text.get_rect(center=(self.WINDOW_WIDTH // 2, self.WINDOW_HEIGHT // 2 - 40))
            self.screen.blit(text, text_rect)
            
            # Final score
            score_text = self.font.render(f"Final Score: {self.steps}", True, self.COLORS['white'])
            score_rect = score_text.get_rect(center=(self.WINDOW_WIDTH // 2, self.WINDOW_HEIGHT // 2 + 10))
            self.screen.blit(score_text, score_rect)
            
            # Press any key to continue
            continue_text = self.font.render("Press any key to continue", True, self.COLORS['white'])
            continue_rect = continue_text.get_rect(center=(self.WINDOW_WIDTH // 2, self.WINDOW_HEIGHT // 2 + 40))
            self.screen.blit(continue_text, continue_rect)
        
        pygame.display.flip()

    def run(self):
        clock = pygame.time.Clock()
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # Handle button clicks
                    button_y = self.PADDING
                    total_button_width = len(self.buttons) * (self.BUTTON_WIDTH + self.BUTTON_SPACING) - self.BUTTON_SPACING
                    start_x = (self.WINDOW_WIDTH - total_button_width) // 2
                    
                    for i, button in enumerate(self.buttons):
                        button_x = start_x + i * (self.BUTTON_WIDTH + self.BUTTON_SPACING)
                        button_rect = pygame.Rect(button_x, button_y, self.BUTTON_WIDTH, self.BUTTON_HEIGHT)
                        
                        if button_rect.collidepoint(event.pos):
                            button["action"]()
                            break
                    
                    # Handle grid clicks for intruder placement
                    if not self.game_running:
                        grid_x = event.pos[0] - self.PADDING
                        grid_y = event.pos[1] - (2 * self.PADDING + self.BUTTON_HEIGHT)
                        if 0 <= grid_x <= self.GRID_SIZE * self.CELL_SIZE and \
                           0 <= grid_y <= self.GRID_SIZE * self.CELL_SIZE:
                            col = grid_x // self.CELL_SIZE
                            row = grid_y // self.CELL_SIZE
                            if (0 <= row < self.GRID_SIZE and 0 <= col < self.GRID_SIZE and
                                self.grid[row][col] == 0 and (row, col) not in self.robots):
                                self.intruder_pos = (row, col)
                
                elif event.type == pygame.KEYDOWN:
                    # Handle game over state
                    if self.game_status == "gameover" and not self.game_running:
                        self.clear_grid()
                        continue

                    if event.key == pygame.K_SPACE and self.intruder_pos and not self.game_running:
                        self.game_running = True
                        self.game_status = "running"
                    
                    if self.game_running:
                        row, col = self.intruder_pos
                        new_row, new_col = row, col
                        moved = False
                        
                        if event.key == pygame.K_UP:
                            new_row -= 1
                            moved = True
                        elif event.key == pygame.K_DOWN:
                            new_row += 1
                            moved = True
                        elif event.key == pygame.K_LEFT:
                            new_col -= 1
                            moved = True
                        elif event.key == pygame.K_RIGHT:
                            new_col += 1
                            moved = True
                        
                        if (0 <= new_row < self.GRID_SIZE and 
                            0 <= new_col < self.GRID_SIZE and 
                            self.grid[new_row][new_col] == 0):
                            self.intruder_pos = (new_row, new_col)
                            if moved:
                                self.steps += 1
                                if self.steps > 0 and self.steps % self.ROBOT_SPEED_INCREASE_STEPS == 0:
                                    self.robot_speed += self.ROBOT_SPEED_INCREASE
            
            self.update_game()
            self.draw()
            clock.tick(60)
        
        pygame.quit()

def main():
    game = GridMaze()
    game.run()

if __name__ == "__main__":
    main()