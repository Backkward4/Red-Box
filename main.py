import pygame
import sys
import keyboard
import asyncio
import os
from pygame.locals import QUIT
from pygame.math import Vector2

pygame.init()

window = Vector2(1000, 600)
screen = pygame.display.set_mode((window.x, window.y))
pygame.display.set_caption("RED BOX")

base_path = os.path.dirname(__file__)

assets = {
    "box": pygame.image.load(os.path.join(base_path, "assets", "box.png")).convert_alpha()
}

center = Vector2(window.x/2, window.y/2)
camera = Vector2(0, 0)
wc = center + camera

gravity = Vector2(0, -9.81)

clock = pygame.time.Clock()

#   custom class for the player, might be simplified for all objects to use polygon instead
class playerBox:
    def __init__(self, rect):
        self.size = 40
        self.rect = pygame.Rect(wc.x - self.size/2, wc.y - self.size/2, self.size, self.size)
        self.pos = Vector2()
        self.velocity = Vector2(0, 0)
        self.rotation = 0
        self.rotationSpeed = 0

redbox = playerBox(0)




async def main():
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == QUIT: # Exit when the window is closed
                running = False
    
        #   world center
        wc = center + camera
        dT = clock.tick(60) / 1000.0
        await asyncio.sleep(0)


        #   applies gravity constantly
        redbox.velocity -= gravity
    
        #   background
        screen.fill((110, 179, 210))

        #   draws redbox where it should be on the screen
        rb_screen = redbox.rect.move(redbox.pos.x + wc.x, redbox.pos.y + wc.y)
#        pygame.draw.rect(screen, (131, 31, 31), rb_screen)
        rb_image = pygame.transform.scale(assets["box"], (redbox.size, redbox.size))
        rb_image = pygame.transform.rotate(rb_image, redbox.rotation)
        rb_pos = (
            rb_screen.x + redbox.size/2,
            rb_screen.y + redbox.size/2
            )
        rb_rect = rb_image.get_rect(center = rb_pos)

        screen.blit(rb_image, rb_rect)
        
        #   creates the border on the player
        redbox_inner = rb_screen.inflate(-10, -10)
#        pygame.draw.rect(screen, (251, 53, 38), redbox_inner)
    
        #   world center box (for reference, will be removed once maps work)
        bgrect = playerBox(1)
        bgrect.size = 200
        bgrect.rect = bgrect.rect.inflate(160, 160)
        bgrect.rect = bgrect.rect.move(
            bgrect.pos.x + wc.x, bgrect.pos.y + wc.y + bgrect.size/2-20
            )
        
        pygame.draw.rect(screen, (11, 11, 11), bgrect)
    
        redbox.rect.x = wc.x - redbox.size/2 + redbox.pos.x - camera.x
        redbox.rect.y = wc.y - redbox.size/2 + redbox.pos.y - camera.y
    
        redbox.pos += redbox.velocity*dT
        #print(redbox.pos) # (debug)
    
        redbox_maxspeed = 150
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
    
        #   stupid way of cancelling out velocity since lerping to 0 wasn't working
        else:
            if redbox.velocity.x > 0.1: 
                redbox.velocity.x = lerp(redbox.velocity.x, -redbox_maxspeed, movementEasing)
            elif redbox.velocity.x < -0.1:
                redbox.velocity.x = lerp(redbox.velocity.x, redbox_maxspeed, movementEasing)
            else:
                redbox.velocity.x = 0

        #   changes redbox rotation
        redbox.rotation -= (redbox.rotationSpeed / (redbox.size/2/100))/180
        print(redbox.rotationSpeed)

        #   handles jumping and ground collision, be changed once actual objects are added
        if redbox.pos.y + redbox.size/2 > 0:
            redbox.rotationSpeed = redbox.velocity.x*2
            
            if keyboard.is_pressed("w"):
                redbox.velocity.y = -230
            else:
                redbox.velocity.y = 0
                redbox.pos.y = 0 - redbox.size/2
        else:
            redbox.rotationSpeed = redbox.rotationSpeed/1.025 + redbox.velocity.x/25
    
        cam_easing = 20
        camera.x = lerp(camera.x, -redbox.pos.x*2 - wc.x - redbox.size/2, cam_easing)
        camera.y = lerp(camera.y, -redbox.pos.y*2 - wc.y + 60 - redbox.size/2, cam_easing)
    
        #print(camera) # (debug)
        
        pygame.display.flip()
        
    # Quit PyGame
    
    pygame.quit()

asyncio.run(main())
