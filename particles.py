"""
This file contains classes for particle effects like confetti, balloons, and glitter.
"""

import pygame
import random
import math

class Particle:
    def __init__(self, x, y, color, size, velocity_x, velocity_y, lifetime):
        self.x = x
        self.y = y
        self.color = color
        self.size = size
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.lifetime = lifetime
        self.age = 0
        
    def update(self):
        self.x += self.velocity_x
        self.y += self.velocity_y
        self.age += 1
        return self.age < self.lifetime
        
    def draw(self, surface):
        alpha = 255 * (1 - self.age / self.lifetime)
        pygame.draw.circle(surface, (*self.color, alpha), (int(self.x), int(self.y)), self.size)

class Confetti:
    def __init__(self, x, y, color, size, velocity_x, velocity_y, lifetime):
        self.x = x
        self.y = y
        self.color = color
        self.size = size
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.lifetime = lifetime
        self.age = 0
        self.rotation = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-5, 5)
        
    def update(self):
        self.x += self.velocity_x
        self.y += self.velocity_y
        self.velocity_y += 0.1  # Gravity
        self.rotation += self.rotation_speed
        self.age += 1
        return self.age < self.lifetime
        
    def draw(self, surface):
        alpha = 255 * (1 - self.age / self.lifetime)
        rect = pygame.Rect(0, 0, self.size, self.size)
        rect.center = (self.x, self.y)
        
        # Create a temporary surface for rotation
        temp_surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.rect(temp_surface, (*self.color, alpha), 
                         pygame.Rect(self.size//2, self.size//2, self.size, self.size))
        
        # Rotate the surface
        rotated_surface = pygame.transform.rotate(temp_surface, self.rotation)
        rotated_rect = rotated_surface.get_rect(center=(self.x, self.y))
        
        # Draw the rotated surface
        surface.blit(rotated_surface, rotated_rect)

class Balloon:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.color = (
            random.randint(100, 255),
            random.randint(100, 255),
            random.randint(100, 255)
        )
        self.size = random.randint(20, 40)
        self.velocity_y = random.uniform(-3, -1)
        self.velocity_x = random.uniform(-0.5, 0.5)
        self.lifetime = random.randint(180, 300)  # 3-5 seconds at 60 FPS
        self.age = 0
        self.wobble = 0
        self.wobble_speed = random.uniform(0.05, 0.1)
        self.wobble_amount = random.uniform(0.5, 2)
        
    def update(self):
        self.y += self.velocity_y
        self.x += self.velocity_x + math.sin(self.wobble) * self.wobble_amount
        self.wobble += self.wobble_speed
        self.age += 1
        return self.age < self.lifetime and self.y > -self.size
        
    def draw(self, surface):
        # Draw balloon
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.size)
        
        # Draw balloon tie
        pygame.draw.polygon(surface, self.color, [
            (self.x, self.y + self.size),
            (self.x - 5, self.y + self.size + 15),
            (self.x + 5, self.y + self.size + 15)
        ])
        
        # Draw string
        pygame.draw.line(surface, (200, 200, 200), 
                         (self.x, self.y + self.size + 15), 
                         (self.x, self.y + self.size + 40), 2)

class ParticleSystem:
    def __init__(self):
        self.particles = []
        self.active = False
        
    def start_celebration(self, screen_width, screen_height):
        self.active = True
        self.particles = []
        
        # Add confetti
        for _ in range(100):
            x = random.randint(0, screen_width)
            y = random.randint(0, screen_height // 2)
            color = (
                random.randint(50, 255),
                random.randint(50, 255),
                random.randint(50, 255)
            )
            size = random.randint(5, 15)
            velocity_x = random.uniform(-2, 2)
            velocity_y = random.uniform(1, 5)
            lifetime = random.randint(120, 240)  # 2-4 seconds at 60 FPS
            self.particles.append(Confetti(x, y, color, size, velocity_x, velocity_y, lifetime))
        
        # Add balloons
        for _ in range(20):
            x = random.randint(0, screen_width)
            y = screen_height + random.randint(10, 50)
            self.particles.append(Balloon(x, y))
        
        # Add glitter particles
        for _ in range(50):
            x = random.randint(0, screen_width)
            y = random.randint(0, screen_height)
            color = (
                random.randint(200, 255),
                random.randint(200, 255),
                random.randint(100, 150)
            )
            size = random.randint(2, 5)
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(1, 3)
            velocity_x = math.cos(angle) * speed
            velocity_y = math.sin(angle) * speed
            lifetime = random.randint(60, 120)  # 1-2 seconds at 60 FPS
            self.particles.append(Particle(x, y, color, size, velocity_x, velocity_y, lifetime))
    
    def update(self):
        if not self.active:
            return
            
        self.particles = [p for p in self.particles if p.update()]
        if not self.particles:
            self.active = False
    
    def draw(self, surface):
        if not self.active:
            return
            
        for particle in self.particles:
            particle.draw(surface)
