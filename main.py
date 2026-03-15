import pygame
import sys
import keyboard
import asyncio
import os
import random
import json
from pygame.locals import QUIT
from pygame.math import Vector2
import tkinter as tk
from tkinter import filedialog

pygame.init()

window = Vector2(1000, 600)
screen = pygame.display.set_mode((window.x, window.y))
pygame.display.set_caption("RED BOX")
pygame.mouse.set_visible(True)

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
cam_zoom = 1
wc = center + camera

gravity = Vector2(0, -15)

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

class Box(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, rot, r, g, b):
        super().__init__()
        self.color = (r, g, b)
        self.pos = Vector2(x, y)
        self.screen_pos = Vector2()
        self.size = Vector2(width, height)


        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.image.fill((255, 100, 50))
        self.rotated_image = pygame.transform.rotate(self.image, rot)

        self.rect = self.rotated_image.get_rect(center = self.screen_pos)
        self.mask = pygame.mask.from_surface(self.rotated_image)


        self.innerimage = pygame.Surface(((max(0, width - 10)), (max(0, height - 10))), pygame.SRCALPHA)
        self.innerimage.fill((255, 100, 50))
        self.rotated_innerimage = pygame.transform.rotate(self.innerimage, rot)

        self.innerrect = self.rotated_image.get_rect(center = self.screen_pos + Vector2(5, 5))
        self.innermask = pygame.mask.from_surface(self.rotated_innerimage)

    def update(self):
        self.screen_pos = self.pos + wc + window/2

        self.rect = self.rotated_image.get_rect(topleft = self.screen_pos)
        self.innerrect = self.rotated_image.get_rect(center = self.screen_pos + Vector2(5, 5))
        
        self.mask = pygame.mask.from_surface(self.rotated_image)
        
        self.visible_mask = self.mask.to_surface(setcolor=(
            self.color[0],
            self.color[1],
            self.color[2],
            255), unsetcolor=(0, 0, 0, 0))
        
    def drawouter(self):
        self.visible_outermask = self.mask.to_surface(setcolor=(
            max(0, self.color[0] - 50), #red
            max(0, self.color[1] - 40), #green
            max(0, self.color[2] - 25), #blue
            255), unsetcolor=(0, 0, 0, 0))
        
        screen.blit(self.visible_outermask, self.screen_pos)
        
    def drawinner(self):
        self.visible_innermask = self.innermask.to_surface(setcolor=(
            self.color[0], self.color[1], self.color[2], 255),
                                                 unsetcolor=(0, 0, 0, 0)
                                                 )
        screen.blit(self.visible_innermask, self.screen_pos + Vector2(5, 5))
        

rb_group = pygame.sprite.Group()
rb_group.add(redbox)

map_group = pygame.sprite.Group()
map_data = []

async def main():
    global camera, wc, shadows_enabled, cam_zoom, map_data
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
        await asyncio.sleep(0)


        #   applies gravity constantly
        redbox.velocity = Vector2(redbox.velocity.x, max(gravity.y*20, redbox.velocity.y - gravity.y))
    
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


        #   custom map loading
        if keyboard.is_pressed("ctrl") and keyboard.is_pressed("shift") and keyboard.is_pressed("p"):
            global map_data, map_data_path
            file_path = filedialog.askopenfilename(title="Select a File", filetypes=[("All Files", "*.*")])
            
            if file_path:
                map_data_path = file_path
                print(f"Selected file: {file_path}")
                
                with open(map_data_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)

                    map_data = data
    
                    print(map_data)

                    for i in map_data:
                        newbox = Box(i[0], i[1], i[2], i[3], i[4], i[5], i[6], i[7])
                        map_group.add(newbox)
                continue

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

        #   update map
        if map_data:
            for i in map_group:
                i.update()

        #   shadows
        if shadows_enabled:
            shadow_canvas = pygame.Surface((window.x, window.y), pygame.SRCALPHA)
            shadow_offset = Vector2(3.5, 11)
            shadow_alpha = 30

            if map_data:
                for i in map_group:
                    shadow_canvas.blit(
                        pygame.mask.from_surface(i.visible_mask).to_surface(setcolor=(0,0,0,255), unsetcolor=(0,0,0,0)),
                        i.screen_pos + shadow_offset)
            
            rb_sil = pygame.mask.from_surface(rb_rotated).to_surface(setcolor=(0,0,0,255), unsetcolor=(0,0,0,0))
            shadow_canvas.blit(rb_sil, redbox.rect.topleft + shadow_offset)

            shadow_canvas.set_alpha(shadow_alpha)
            screen.blit(shadow_canvas, (0, 0))


        #screen.blit(cur_map.image, cur_map.rect.topleft)

        if map_data:
            for i in map_group:
                i.drawouter()
                                         
            for i in map_group:
                i.drawinner()
                                         
                
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
                redbox.velocity.y = -300 # jump height
            else:
                redbox.pos = redbox_lastpos
                redbox.velocity.y = 0
                
        else:
            redbox.rotationSpeed = redbox.rotationSpeed/1.05 + redbox.velocity.x/30
    
        cam_easing = 20
        camera.x = lerp(camera.x, -redbox.pos.x*2 - wc.x - redbox.size/2, cam_easing)
        camera.y = lerp(camera.y, -redbox.pos.y*2 - wc.y - redbox.size/2 + 60, cam_easing)

        if keyboard.is_pressed("ctrl") and keyboard.is_pressed("s"):
            if not temp:
                shadows_enabled = not shadows_enabled
                temp = True
        else:
            temp = False

        if keyboard.is_pressed("up"):
            cam_zoom = min(2, cam_zoom + 0.5)
            
        if keyboard.is_pressed("down"):
            cam_zoom = max(0.25, cam_zoom - 0.5)

        if keyboard.is_pressed("r"):
            redbox.velocity = Vector2(0, 0)
            redbox.pos = Vector2(0, 0)
            #camera = Vector2(redbox.pos.x - 500, -200)

        pygame.display.flip()

    # Quit PyGame
    pygame.quit()


asyncio.run(main())
