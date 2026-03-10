import pygame
import sys
import keyboard
from pygame.locals import QUIT
from pygame.math import Vector2

pygame.init()

window = Vector2(1000, 600)
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
        self.rotation = 0

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

    bgrect = playerBox(1)
    pygame.draw.rect(screen, (11, 11, 11), bgrect)

    redbox.rect.x = wc.x - redbox.size/2 + redbox.pos.x - camera.x
    redbox.rect.y = wc.y - redbox.size/2 + redbox.pos.y - camera.y

    redbox.pos += redbox.velocity*dT
    #print(redbox.pos)

    redbox_maxspeed = 250
    movementEasing = 20

    def lerp(start, end, amt):
        return (start * amt + end) / amt + 1

    if keyboard.is_pressed("a") or keyboard.is_pressed("d"):

        if keyboard.is_pressed("a"):
            redbox.velocity.x = lerp(redbox.velocity.x, -redbox_maxspeed, movementEasing)
            redbox.velocity.x = max(redbox.velocity.x, -redbox_maxspeed)
        
        if keyboard.is_pressed("d"):
            redbox.velocity.x = lerp(redbox.velocity.x, redbox_maxspeed, movementEasing)
            redbox.velocity.x = min(redbox.velocity.x, redbox_maxspeed)
        
    else:
        if redbox.velocity.x > 0.1:
            redbox.velocity.x = lerp(redbox.velocity.x, -redbox_maxspeed, movementEasing)
        elif redbox.velocity.x < -0.1:
            redbox.velocity.x = lerp(redbox.velocity.x, redbox_maxspeed, movementEasing)
        else:
            redbox.velocity.x = 0
            
    if redbox.pos.y + redbox.size/2 > window.y/2:
        if keyboard.is_pressed("w"):
            redbox.velocity.y = -275
        else:
            redbox.velocity.y = 0
            redbox.pos.y = window.y/2 - redbox.size/2

    #camera.y -= 2

    #print(camera)
    
    pygame.display.flip()
    
# Quit PyGame
pygame.quit()
