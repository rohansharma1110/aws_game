"""
This file contains a function to generate an AWS logo as a pygame surface.
Since we can't download external images, we'll create a simple AWS logo programmatically.
"""

import pygame

def create_aws_logo(width=200, height=100):
    """Create a simple AWS logo as a pygame surface"""
    logo = pygame.Surface((width, height), pygame.SRCALPHA)
    
    # AWS Orange color
    aws_orange = (255, 153, 0)
    
    # Draw the AWS text
    font = pygame.font.SysFont('Arial', int(height * 0.6), bold=True)
    aws_text = font.render("AWS", True, aws_orange)
    text_rect = aws_text.get_rect(center=(width//2, height//2))
    logo.blit(aws_text, text_rect)
    
    # Draw a simple cloud shape around the text
    pygame.draw.ellipse(logo, (255, 255, 255, 80), (width * 0.1, height * 0.2, width * 0.8, height * 0.6), 3)
    
    return logo
