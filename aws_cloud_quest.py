import pygame
import sys
import random
import json
import time
import os
import math
from pygame.locals import *

# Initialize pygame
pygame.init()
pygame.font.init()

# Constants
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (66, 133, 244)  # AWS Blue
ORANGE = (255, 153, 0)  # AWS Orange
LIGHT_BLUE = (135, 206, 250)
GRAY = (200, 200, 200)
GREEN = (0, 200, 0)
RED = (200, 0, 0)

# Create assets directory if it doesn't exist
ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
if not os.path.exists(ASSETS_DIR):
    os.makedirs(ASSETS_DIR)

# Game states
MENU = 0
GAME_MODE = 1
DIFFICULTY = 2
WAITING = 3
PLAYING = 4
RESULT = 5
CREDITS = 6

# Import custom modules
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets"))
try:
    from assets.aws_logo import create_aws_logo
    from assets.particles import ParticleSystem
except ImportError:
    # Fallback if imports fail
    def create_aws_logo(width=200, height=100):
        logo = pygame.Surface((width, height))
        logo.fill(ORANGE)
        return logo
    
    class ParticleSystem:
        def __init__(self):
            self.active = False
        def start_celebration(self, width, height):
            self.active = True
        def update(self):
            pass
        def draw(self, surface):
            pass

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.current_color = color
        self.font = pygame.font.SysFont('Arial', 24)
        
    def draw(self, screen):
        pygame.draw.rect(screen, self.current_color, self.rect, border_radius=10)
        pygame.draw.rect(screen, BLACK, self.rect, 2, border_radius=10)
        text_surface = self.font.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
        
    def is_hovered(self, pos):
        if self.rect.collidepoint(pos):
            self.current_color = self.hover_color
            return True
        self.current_color = self.color
        return False

class AWSCloudQuest:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("AWS Cloud Quest")
        self.clock = pygame.time.Clock()
        self.state = MENU
        self.player_name = ""
        self.game_code = ""
        self.difficulty = ""
        self.score = 0
        self.opponent_score = 0
        self.current_question = 0
        self.questions = []
        self.selected_answer = None
        self.correct_answer = None
        self.answer_time = 0
        self.result_message = ""
        self.is_multiplayer = False
        self.input_active = False
        self.load_questions()
        
        # Initialize particle system for celebrations
        self.particle_system = ParticleSystem()
        
        # Load AWS cloud background image (placeholder)
        self.background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.background.fill(LIGHT_BLUE)
        
        # Create cloud patterns in the background
        for _ in range(15):
            cloud_x = random.randint(0, SCREEN_WIDTH)
            cloud_y = random.randint(0, SCREEN_HEIGHT)
            cloud_size = random.randint(50, 150)
            pygame.draw.ellipse(self.background, (255, 255, 255, 128), 
                               (cloud_x, cloud_y, cloud_size, cloud_size//2), 0)
        
        # Create AWS logo
        self.logo = create_aws_logo(200, 100)
        
        # Create buttons
        self.menu_buttons = [
            Button(SCREEN_WIDTH//2 - 150, 300, 300, 60, "Start Game", ORANGE, LIGHT_BLUE),
            Button(SCREEN_WIDTH//2 - 150, 380, 300, 60, "Credits", ORANGE, LIGHT_BLUE),
            Button(SCREEN_WIDTH//2 - 150, 460, 300, 60, "Quit", ORANGE, LIGHT_BLUE)
        ]
        
        self.game_mode_buttons = [
            Button(SCREEN_WIDTH//2 - 150, 300, 300, 60, "Single Player", ORANGE, LIGHT_BLUE),
            Button(SCREEN_WIDTH//2 - 150, 380, 300, 60, "Multiplayer", ORANGE, LIGHT_BLUE),
            Button(SCREEN_WIDTH//2 - 150, 460, 300, 60, "Back", ORANGE, LIGHT_BLUE)
        ]
        
        self.difficulty_buttons = [
            Button(SCREEN_WIDTH//2 - 150, 300, 300, 60, "Beginner", ORANGE, LIGHT_BLUE),
            Button(SCREEN_WIDTH//2 - 150, 380, 300, 60, "Intermediate", ORANGE, LIGHT_BLUE),
            Button(SCREEN_WIDTH//2 - 150, 460, 300, 60, "Hard", ORANGE, LIGHT_BLUE),
            Button(SCREEN_WIDTH//2 - 150, 540, 300, 60, "Back", ORANGE, LIGHT_BLUE)
        ]
        
        self.result_buttons = [
            Button(SCREEN_WIDTH//2 - 150, 500, 300, 60, "Play Again", ORANGE, LIGHT_BLUE),
            Button(SCREEN_WIDTH//2 - 150, 580, 300, 60, "Main Menu", ORANGE, LIGHT_BLUE)
        ]
        
        self.credits_buttons = [
            Button(SCREEN_WIDTH//2 - 150, 580, 300, 60, "Back", ORANGE, LIGHT_BLUE)
        ]
        
        # Fonts
        self.title_font = pygame.font.SysFont('Arial', 48, bold=True)
        self.subtitle_font = pygame.font.SysFont('Arial', 36)
        self.text_font = pygame.font.SysFont('Arial', 24)
        self.question_font = pygame.font.SysFont('Arial', 28)
        
    def load_questions(self):
        # Sample questions - in a real implementation, load from a JSON file
        self.all_questions = {
            "Beginner": [
                {
                    "question": "What is the AWS service for object storage?",
                    "options": ["S3", "EC2", "RDS", "Lambda"],
                    "answer": 0
                },
                {
                    "question": "Which AWS service provides virtual servers in the cloud?",
                    "options": ["S3", "EC2", "DynamoDB", "CloudFront"],
                    "answer": 1
                },
                {
                    "question": "What does IAM stand for in AWS?",
                    "options": ["Internet Access Management", "Identity and Access Management", "Internal Account Manager", "Infrastructure Asset Management"],
                    "answer": 1
                },
                {
                    "question": "Which AWS service is used for relational databases?",
                    "options": ["DynamoDB", "S3", "RDS", "SQS"],
                    "answer": 2
                },
                {
                    "question": "What is the AWS global infrastructure component where data centers are located?",
                    "options": ["Edge Locations", "Regions", "Availability Zones", "Data Centers"],
                    "answer": 1
                }
            ],
            "Intermediate": [
                {
                    "question": "Which AWS service would you use for serverless computing?",
                    "options": ["EC2", "Lambda", "ECS", "Lightsail"],
                    "answer": 1
                },
                {
                    "question": "What AWS service provides a virtual private cloud?",
                    "options": ["VPC", "CloudFront", "Route 53", "Direct Connect"],
                    "answer": 0
                },
                {
                    "question": "Which AWS service is used for NoSQL databases?",
                    "options": ["RDS", "Redshift", "DynamoDB", "Aurora"],
                    "answer": 2
                },
                {
                    "question": "What AWS service provides content delivery network (CDN) functionality?",
                    "options": ["S3", "CloudFront", "Route 53", "API Gateway"],
                    "answer": 1
                },
                {
                    "question": "Which AWS service is used for DNS management?",
                    "options": ["CloudFront", "Route 53", "CloudFormation", "CloudWatch"],
                    "answer": 1
                }
            ],
            "Hard": [
                {
                    "question": "Which AWS service would you use for infrastructure as code?",
                    "options": ["CloudFormation", "OpsWorks", "Elastic Beanstalk", "Systems Manager"],
                    "answer": 0
                },
                {
                    "question": "What is the AWS shared responsibility model?",
                    "options": [
                        "AWS is responsible for everything",
                        "Customer is responsible for everything",
                        "AWS is responsible for the cloud, customer is responsible for what's in the cloud",
                        "AWS and customer share all responsibilities equally"
                    ],
                    "answer": 2
                },
                {
                    "question": "Which AWS service provides a fully managed Hadoop framework?",
                    "options": ["Redshift", "EMR", "Athena", "Glue"],
                    "answer": 1
                },
                {
                    "question": "What AWS service would you use for real-time data streaming?",
                    "options": ["SQS", "SNS", "Kinesis", "EventBridge"],
                    "answer": 2
                },
                {
                    "question": "Which AWS service provides a hybrid cloud storage solution?",
                    "options": ["S3", "EFS", "Storage Gateway", "FSx"],
                    "answer": 2
                }
            ]
        }
    
    def set_questions(self, difficulty):
        self.difficulty = difficulty
        self.questions = self.all_questions[difficulty].copy()
        random.shuffle(self.questions)
        self.current_question = 0
        self.score = 0
        self.opponent_score = 0
        
    def draw_text_input(self, prompt, input_text):
        prompt_surface = self.subtitle_font.render(prompt, True, BLACK)
        prompt_rect = prompt_surface.get_rect(center=(SCREEN_WIDTH//2, 250))
        self.screen.blit(prompt_surface, prompt_rect)
        
        input_box = pygame.Rect(SCREEN_WIDTH//2 - 150, 300, 300, 60)
        pygame.draw.rect(self.screen, WHITE, input_box, border_radius=10)
        pygame.draw.rect(self.screen, BLACK, input_box, 2, border_radius=10)
        
        input_surface = self.text_font.render(input_text, True, BLACK)
        input_rect = input_surface.get_rect(center=input_box.center)
        self.screen.blit(input_surface, input_rect)
        
    def simulate_opponent(self):
        # Simulate opponent answering questions (randomly)
        if random.random() > 0.3:  # 70% chance of correct answer
            self.opponent_score += 100 + random.randint(0, 50)  # Random bonus points
            
    def draw_menu(self):
        # Draw title
        title_surface = self.title_font.render("AWS Cloud Quest", True, BLACK)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH//2, 150))
        self.screen.blit(title_surface, title_rect)
        
        # Draw buttons
        for button in self.menu_buttons:
            button.draw(self.screen)
            
    def draw_game_mode(self):
        # Draw title
        title_surface = self.title_font.render("Select Game Mode", True, BLACK)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH//2, 150))
        self.screen.blit(title_surface, title_rect)
        
        # Draw buttons
        for button in self.game_mode_buttons:
            button.draw(self.screen)
            
    def draw_difficulty(self):
        # Draw title
        title_surface = self.title_font.render("Select Difficulty", True, BLACK)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH//2, 150))
        self.screen.blit(title_surface, title_rect)
        
        # Draw buttons
        for button in self.difficulty_buttons:
            button.draw(self.screen)
            
    def draw_waiting(self):
        # Draw title
        title_surface = self.title_font.render("Waiting for Opponent", True, BLACK)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH//2, 150))
        self.screen.blit(title_surface, title_rect)
        
        # Draw game code
        code_text = f"Game Code: {self.game_code}"
        code_surface = self.subtitle_font.render(code_text, True, BLACK)
        code_rect = code_surface.get_rect(center=(SCREEN_WIDTH//2, 250))
        self.screen.blit(code_surface, code_rect)
        
        # Draw loading animation (simple text for now)
        dots = "." * (int(time.time() * 2) % 4)
        loading_surface = self.text_font.render(f"Waiting{dots}", True, BLACK)
        loading_rect = loading_surface.get_rect(center=(SCREEN_WIDTH//2, 350))
        self.screen.blit(loading_surface, loading_rect)
        
        # In a real implementation, check for opponent connection
        # For demo, automatically connect after a few seconds
        if time.time() % 5 < 0.1:
            self.state = PLAYING
            
    def draw_playing(self):
        if self.current_question >= len(self.questions):
            self.state = RESULT
            if self.score > self.opponent_score:
                self.result_message = "Congratulations! You Won!"
            elif self.score < self.opponent_score:
                self.result_message = "You Lost. Try Again!"
            else:
                self.result_message = "It's a Tie!"
            return
            
        # Draw question number and difficulty
        header_text = f"Question {self.current_question + 1}/{len(self.questions)} - {self.difficulty}"
        header_surface = self.subtitle_font.render(header_text, True, BLACK)
        header_rect = header_surface.get_rect(topleft=(50, 50))
        self.screen.blit(header_surface, header_rect)
        
        # Draw scores
        score_text = f"Your Score: {self.score}"
        score_surface = self.text_font.render(score_text, True, BLACK)
        score_rect = score_surface.get_rect(topleft=(50, 100))
        self.screen.blit(score_surface, score_rect)
        
        if self.is_multiplayer:
            opponent_text = f"Opponent Score: {self.opponent_score}"
            opponent_surface = self.text_font.render(opponent_text, True, BLACK)
            opponent_rect = opponent_surface.get_rect(topright=(SCREEN_WIDTH - 50, 100))
            self.screen.blit(opponent_surface, opponent_rect)
        
        # Draw question
        question = self.questions[self.current_question]["question"]
        question_surface = self.question_font.render(question, True, BLACK)
        question_rect = question_surface.get_rect(center=(SCREEN_WIDTH//2, 200))
        self.screen.blit(question_surface, question_rect)
        
        # Draw options
        options = self.questions[self.current_question]["options"]
        for i, option in enumerate(options):
            option_rect = pygame.Rect(SCREEN_WIDTH//2 - 300, 300 + i*80, 600, 60)
            
            # Highlight selected answer
            if self.selected_answer == i:
                pygame.draw.rect(self.screen, ORANGE, option_rect, border_radius=10)
            else:
                pygame.draw.rect(self.screen, WHITE, option_rect, border_radius=10)
                
            pygame.draw.rect(self.screen, BLACK, option_rect, 2, border_radius=10)
            
            option_surface = self.text_font.render(f"{chr(65+i)}. {option}", True, BLACK)
            option_text_rect = option_surface.get_rect(midleft=(option_rect.left + 20, option_rect.centery))
            self.screen.blit(option_surface, option_text_rect)
            
        # Draw timer (if implemented)
        # timer_text = f"Time: {30 - int(time.time() - self.answer_time)}"
        # timer_surface = self.text_font.render(timer_text, True, BLACK)
        # timer_rect = timer_surface.get_rect(topright=(SCREEN_WIDTH - 50, 50))
        # self.screen.blit(timer_surface, timer_rect)
        
    def draw_result(self):
        # Draw title
        title_surface = self.title_font.render("Game Results", True, BLACK)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH//2, 150))
        self.screen.blit(title_surface, title_rect)
        
        # Draw result message
        result_surface = self.subtitle_font.render(self.result_message, True, BLACK)
        result_rect = result_surface.get_rect(center=(SCREEN_WIDTH//2, 250))
        self.screen.blit(result_surface, result_rect)
        
        # Draw scores
        score_text = f"Your Score: {self.score}"
        score_surface = self.text_font.render(score_text, True, BLACK)
        score_rect = score_surface.get_rect(center=(SCREEN_WIDTH//2, 320))
        self.screen.blit(score_surface, score_rect)
        
        if self.is_multiplayer:
            opponent_text = f"Opponent Score: {self.opponent_score}"
            opponent_surface = self.text_font.render(opponent_text, True, BLACK)
            opponent_rect = opponent_surface.get_rect(center=(SCREEN_WIDTH//2, 370))
            self.screen.blit(opponent_surface, opponent_rect)
        
        # Draw buttons
        for button in self.result_buttons:
            button.draw(self.screen)
            
        # Draw celebration particles if player won
        if "Congratulations" in self.result_message:
            if not self.particle_system.active:
                self.particle_system.start_celebration(SCREEN_WIDTH, SCREEN_HEIGHT)
            self.particle_system.draw(self.screen)
            
    def draw_credits(self):
        # Draw title
        title_surface = self.title_font.render("Credits", True, BLACK)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH//2, 100))
        self.screen.blit(title_surface, title_rect)
        
        # Draw credits text
        credits = [
            "Developer: Rohan Sharma",
            "In Partnership With: Amazon Web Services",
            "",
            "Special Thanks:",
            "AWS Cloud Practitioner Community",
            "",
            "© 2025 Rohan Sharma | AWS Cloud Quest"
        ]
        
        for i, line in enumerate(credits):
            credit_surface = self.text_font.render(line, True, BLACK)
            credit_rect = credit_surface.get_rect(center=(SCREEN_WIDTH//2, 200 + i*40))
            self.screen.blit(credit_surface, credit_rect)
        
        # Draw buttons
        for button in self.credits_buttons:
            button.draw(self.screen)
            
    def handle_menu_click(self, pos):
        for i, button in enumerate(self.menu_buttons):
            if button.rect.collidepoint(pos):
                if i == 0:  # Start Game
                    self.state = GAME_MODE
                elif i == 1:  # Credits
                    self.state = CREDITS
                elif i == 2:  # Quit
                    pygame.quit()
                    sys.exit()
                    
    def handle_game_mode_click(self, pos):
        for i, button in enumerate(self.game_mode_buttons):
            if button.rect.collidepoint(pos):
                if i == 0:  # Single Player
                    self.is_multiplayer = False
                    self.state = DIFFICULTY
                elif i == 1:  # Multiplayer
                    self.is_multiplayer = True
                    self.state = DIFFICULTY
                    # In a real implementation, handle player name input and game code generation
                    self.game_code = "".join([str(random.randint(0, 9)) for _ in range(6)])
                elif i == 2:  # Back
                    self.state = MENU
                    
    def handle_difficulty_click(self, pos):
        for i, button in enumerate(self.difficulty_buttons):
            if button.rect.collidepoint(pos):
                if i == 0:  # Beginner
                    self.set_questions("Beginner")
                    if self.is_multiplayer:
                        self.state = WAITING
                    else:
                        self.state = PLAYING
                        self.answer_time = time.time()
                elif i == 1:  # Intermediate
                    self.set_questions("Intermediate")
                    if self.is_multiplayer:
                        self.state = WAITING
                    else:
                        self.state = PLAYING
                        self.answer_time = time.time()
                elif i == 2:  # Hard
                    self.set_questions("Hard")
                    if self.is_multiplayer:
                        self.state = WAITING
                    else:
                        self.state = PLAYING
                        self.answer_time = time.time()
                elif i == 3:  # Back
                    self.state = GAME_MODE
                    
    def handle_playing_click(self, pos):
        options = self.questions[self.current_question]["options"]
        for i in range(len(options)):
            option_rect = pygame.Rect(SCREEN_WIDTH//2 - 300, 300 + i*80, 600, 60)
            if option_rect.collidepoint(pos):
                self.selected_answer = i
                correct_answer = self.questions[self.current_question]["answer"]
                
                # Calculate score based on correctness and time
                if self.selected_answer == correct_answer:
                    time_bonus = max(0, 50 - int(time.time() - self.answer_time))
                    self.score += 100 + time_bonus
                
                # Simulate opponent answer
                if self.is_multiplayer:
                    self.simulate_opponent()
                
                # Move to next question after a short delay
                pygame.time.delay(1000)  # 1 second delay to show the selected answer
                self.current_question += 1
                self.selected_answer = None
                self.answer_time = time.time()
                break
                
    def handle_result_click(self, pos):
        for i, button in enumerate(self.result_buttons):
            if button.rect.collidepoint(pos):
                if i == 0:  # Play Again
                    self.state = DIFFICULTY
                elif i == 1:  # Main Menu
                    self.state = MENU
                    
    def handle_credits_click(self, pos):
        for button in self.credits_buttons:
            if button.rect.collidepoint(pos):
                self.state = MENU
                
    def run(self):
        running = True
        while running:
            mouse_pos = pygame.mouse.get_pos()
            
            # Handle events
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                elif event.type == MOUSEBUTTONDOWN:
                    if self.state == MENU:
                        self.handle_menu_click(event.pos)
                    elif self.state == GAME_MODE:
                        self.handle_game_mode_click(event.pos)
                    elif self.state == DIFFICULTY:
                        self.handle_difficulty_click(event.pos)
                    elif self.state == PLAYING:
                        self.handle_playing_click(event.pos)
                    elif self.state == RESULT:
                        self.handle_result_click(event.pos)
                    elif self.state == CREDITS:
                        self.handle_credits_click(event.pos)
                        
            # Draw background
            self.screen.blit(self.background, (0, 0))
            
            # Draw AWS logo in the top-left corner
            self.screen.blit(self.logo, (20, 20))
            
            # Draw current state
            if self.state == MENU:
                self.draw_menu()
            elif self.state == GAME_MODE:
                self.draw_game_mode()
            elif self.state == DIFFICULTY:
                self.draw_difficulty()
            elif self.state == WAITING:
                self.draw_waiting()
            elif self.state == PLAYING:
                self.draw_playing()
            elif self.state == RESULT:
                self.draw_result()
                # Update particle system
                self.particle_system.update()
            elif self.state == CREDITS:
                self.draw_credits()
                
            # Update button hover states
            if self.state == MENU:
                for button in self.menu_buttons:
                    button.is_hovered(mouse_pos)
            elif self.state == GAME_MODE:
                for button in self.game_mode_buttons:
                    button.is_hovered(mouse_pos)
            elif self.state == DIFFICULTY:
                for button in self.difficulty_buttons:
                    button.is_hovered(mouse_pos)
            elif self.state == RESULT:
                for button in self.result_buttons:
                    button.is_hovered(mouse_pos)
            elif self.state == CREDITS:
                for button in self.credits_buttons:
                    button.is_hovered(mouse_pos)
                    
            # Update display
            pygame.display.flip()
            self.clock.tick(60)
            
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = AWSCloudQuest()
    game.run()
