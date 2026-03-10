import pygame
import sys
from pygame.locals import QUIT
from pygame.math import Vector2

pygame.init()

window = Vector2(640, 480)
screen = pygame.display.set_mode((window.x, window.y))
pygame.display.set_caption("RED BOX")
center = Vector2(window.x/2, window.y/2)

camera = Vector2(0, 0)
wc = center + camera

gravity = Vector2(0, -9.81)

clock = pygame.time.Clock()

class playerBox:
    def __init__(self, rect):
        self.size = 40
        self.rect = pygame.Rect(wc.x - self.size/2, wc.y - self.size/2, self.size, self.size)
        self.pos = Vector2()
        self.velocity = Vector2(0, 0)

redbox = playerBox(0)

# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == QUIT: # Exit when the window is closed
            running = False
            
    wc = center + camera
    dT = clock.tick(60) / 1000.0

    redbox.velocity -= gravity
    
    screen.fill((0, 0, 0))
    pygame.draw.rect(screen, (251, 53, 38), redbox)

    redbox.rect.x = wc.x - redbox.size/2 + redbox.pos.x - camera.x
    redbox.rect.y = wc.y - redbox.size/2 + redbox.pos.y - camera.y

    redbox.pos += redbox.velocity*dT
    #print(redbox.pos)

    #camera.y -= 2

    #print(camera)
    
    pygame.display.flip()
    
# Quit PyGame
pygame.quit()
