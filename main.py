import pygame
import sys
import keyboard
import asyncio
import os
import random
from pygame.locals import QUIT
from pygame.math import Vector2
import tkinter as tk
from tkinter import filedialog

pygame.init()

window = Vector2(1000, 600)
screen = pygame.display.set_mode((window.x, window.y))
pygame.display.set_caption("RED BOX")
pygame.mouse.set_visible(False)

root = tk.Tk()
root.withdraw()

base_path = os.path.dirname(__file__)


assets = {
    "box": pygame.image.load(os.path.join(base_path, "assets", "box.png")).convert_alpha(),
    "cloud1": pygame.image.load(os.path.join(base_path, "assets", "cloud1.png")).convert_alpha(),
    "cloud2": pygame.image.load(os.path.join(base_path, "assets", "cloud2.png")).convert_alpha(),
    "DayFace": pygame.image.load(os.path.join(base_path, "assets", "DayFace.png")).convert_alpha(),
    "DayBG": pygame.image.load(os.path.join(base_path, "assets", "DayBG.png")).convert_alpha()
}

maps = {
    "testlevel": pygame.image.load(os.path.join(base_path, "maps", "testlevel.png")).convert_alpha(),
}

window_icon = pygame.transform.scale(assets["box"], (32, 32))
pygame.display.set_icon(window_icon)

center = Vector2(window.x/2, window.y/2)
camera = Vector2(0, 0)
wc = center + camera

gravity = Vector2(0, -9.81)

clock = pygame.time.Clock()

#   custom class for the player, might be simplified for all objects to use polygon instead
class playerBox(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.size = 40
        self.image = assets["box"]
        self.image = pygame.transform.scale(self.image, (self.size, self.size))
        #self.rect = pygame.Rect(wc.x - self.size/2, wc.y - self.size/2, self.size, self.size)
        self.rect = self.image.get_rect(topleft = (x, y))
        self.pos = Vector2()
        self.mask = pygame.mask.from_surface(self.image)
        self.velocity = Vector2(0, 0)
        self.rotation = 0
        self.rotationSpeed = 0
        
redbox = playerBox(window.x/2, window.y/2)

class Map(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = maps["testlevel"]
        self.rect = self.image.get_rect(topleft = (x, y))
        self.pos = Vector2()
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, filepath):
        global camera
        redbox.pos = Vector2(-230, -250)
        redbox.velocity = Vector2(0, 0)
        camera = Vector2(-230, -250)
        self.image = pygame.image.load(filepath).convert_alpha()
        self.mask = pygame.mask.from_surface(self.image)
        
cur_map = Map(0, 0)

rb_group = pygame.sprite.Group()
map_group = pygame.sprite.Group()

rb_group.add(redbox)
map_group.add(cur_map)

async def main():
    global camera, wc, shadows_enabled
    cloud_group = pygame.sprite.Group()
    shadows_enabled = True
    loading = False
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == QUIT: # Exit when the window is closed
                running = False

        if loading:
            await asyncio.sleep(0)
            print("loading")
            return
    
        #   world center
        wc = center + camera
        dT = clock.tick(60) / 1000.0
        print(dT)
        await asyncio.sleep(0)


        #   applies gravity constantly
        redbox.velocity -= gravity
    
        #   fallback background
        screen.fill((110, 179, 210))

        #   actual background
        bg_image = pygame.transform.scale(assets["DayBG"], (window.x, window.y))
        bg_pos = Vector2(window.x/2, window.y/2)
        bg_rect = bg_image.get_rect(center = bg_pos)
        screen.blit(bg_image, bg_rect)

        #   background elements
        bg_face_size = 450
        bg_face = pygame.transform.scale(assets["DayFace"], (bg_face_size, bg_face_size))
        bg_face_pos = Vector2(
            camera.x/50 + wc.x/50 + window.x/2 - bg_face_size/2 + 225,
            camera.y/50 + wc.y/50 + window.y/2 - bg_face_size/2 + 160
            )
        bg_face_rect = bg_face.get_rect(center = bg_face_pos)

        screen.blit(bg_face, bg_face_rect)

        #print(redbox.pos)
        #print(cur_map.pos)
        
        # Clouds
        cloud_amount = 3
        cloud_minsize = 1
        cloud_maxsize = 1
        
        class Cloud(pygame.sprite.Sprite):
            def __init__(self, x, y):
                pygame.sprite.Sprite.__init__(self)
                self.scale = Vector2(
                    random.uniform(cloud_minsize, cloud_maxsize),
                    random.uniform(cloud_minsize, cloud_maxsize)/2
                    )
                self.image = assets["cloud" + str(random.randint(1, 2))]
                self.image_scaled = pygame.transform.scale(
                    assets["cloud" + str(random.randint(1, 2))], (int(self.scale.x), int(self.scale.y))
                    )
                self.speed = random.uniform(0.2, 1)
                self.rect = self.image_scaled.get_rect()
                self.temp_center = [x, y]
                self.rect.center = Vector2(
            camera.x/5 + wc.x/5 + window.x/2 - self.scale.x/2 + self.temp_center[0],
            camera.y/5 + wc.y/5 + window.y/2 - self.scale.y/2 + self.temp_center[1]
            )

            def update(self):
                self.temp_center[0] -= 1
                self.rect.center = Vector2(
            camera.x/15 + wc.x/15 + window.x/2 - self.scale.x/2 + self.temp_center[0],
            camera.y/15 + wc.y/15 + window.y/2 - self.scale.y/2 + self.temp_center[1]
            )
                self.image.set_alpha(int(abs(self.rect.center[0] - bg_face_pos.x + bg_face_size/8)/3))

        cloud_group.update()
        cloud_group.draw(screen)


        cur_map.pos = wc + Vector2(
            cur_map.image.get_width()/2,
            cur_map.image.get_height()/2
            )
        cur_map.rect = cur_map.image.get_rect(center = cur_map.pos)

        
        if len(cloud_group) < cloud_amount:
            newcloud = Cloud(random.uniform(200, 600), random.uniform(-100, -200))
            cloud_group.add(newcloud)

        #   draws redbox where it should be on the screen
        redbox_lastpos = redbox.pos

        redbox.pos += redbox.velocity*dT
        rb_rotated = pygame.transform.rotate(redbox.image, redbox.rotation)

        redbox.rect.center = (int(redbox.pos.x), int(redbox.pos.y))
        target_center = wc - camera + redbox.pos + wc/2 + Vector2(
            redbox.size,
            redbox.size)/2
        
        redbox_old_center = redbox.rect.center
        redbox.rect = rb_rotated.get_rect(center = (int(target_center.x), int(target_center.y)))

        redbox.mask = pygame.mask.from_surface(rb_rotated)
        
        redbox_maxspeed = 200
        movementEasing = 20

        #   shadows
        if shadows_enabled:
            shadow_canvas = pygame.Surface((window.x, window.y), pygame.SRCALPHA)
            shadow_offset = Vector2(3.5, 11)
            shadow_alpha = 30
            
            map_sil = pygame.mask.from_surface(cur_map.image).to_surface(setcolor=(0,0,0,255), unsetcolor=(0,0,0,0))
            shadow_canvas.blit(map_sil, cur_map.rect.topleft + shadow_offset)
            rb_sil = pygame.mask.from_surface(rb_rotated).to_surface(setcolor=(0,0,0,255), unsetcolor=(0,0,0,0))
            shadow_canvas.blit(rb_sil, redbox.rect.topleft + shadow_offset)

            shadow_canvas.set_alpha(shadow_alpha)
            screen.blit(shadow_canvas, (0, 0))


        screen.blit(cur_map.image, cur_map.rect.topleft)
        screen.blit(rb_rotated, redbox.rect.topleft)
    
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
        
        #   ground collision
        if pygame.sprite.spritecollide(redbox, map_group, False, pygame.sprite.collide_mask):
            redbox.rotationSpeed = redbox.velocity.x*2
            
            if keyboard.is_pressed("w"):
                redbox.velocity.y = -175 # jump height
            else:
                redbox.pos = redbox_lastpos
                redbox.velocity.y = 0
                
        else:
            redbox.rotationSpeed = redbox.rotationSpeed/1.05 + redbox.velocity.x/30
    
        cam_easing = 20
        camera.x = lerp(camera.x, -redbox.pos.x*2 - wc.x - redbox.size/2, cam_easing)
        camera.y = lerp(camera.y, -redbox.pos.y*2 - wc.y - redbox.size/2 + 60, cam_easing)

        #   custom map loading
        if keyboard.is_pressed("ctrl") and keyboard.is_pressed("shift") and keyboard.is_pressed("p"):
            file_path = filedialog.askopenfilename(title="Select a File", filetypes=[("All Files", "*.*")])
            
            if file_path:
                cur_map.update(file_path)
                print(f"Selected file: {file_path}")
                continue

        if keyboard.is_pressed("ctrl") and keyboard.is_pressed("s"):
            if not temp:
                shadows_enabled = not shadows_enabled
                temp = True
        else:
            temp = False

        if keyboard.is_pressed("r"):
            redbox.velocity = Vector2(0, 0)
            redbox.pos = Vector2(0, 0)
            #camera = Vector2(redbox.pos.x - 500, -200)

        pygame.display.flip()

    # Quit PyGame
    pygame.quit()


asyncio.run(main())
