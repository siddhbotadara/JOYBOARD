# player.py
# Importing needed files
import warnings
warnings.filterwarnings("ignore", category=UserWarning)
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"
import pygame
from pygame.sprite import Group
from settings import *
from tiles import main_tile_group
from input_module import get_joystick_2_x,get_joystick_1_y

# Define 2D vector
vector = pygame.math.Vector2

# Global variables to store preloaded sprites
_PLAYER_RUN_SPRITES, _PLAYER_RUN_LEFT_SPRITES,_PLAYER_RUN_MASKS_RIGHT,_PLAYER_RUN_MASKS_LEFT = [], [],[], []
_PLAYER_IDLE_SPRITES, _PLAYER_IDLE_LEFT_SPRITES, _PLAYER_IDLE_MASKS_RIGHT, _PLAYER_IDLE_MASKS_LEFT = [], [], [], []
_PLAYER_SHOOT_POSITION, _PLAYER_SHOOT_POSITION_LEFT, _PLAYER_SHOOT_MASKS_RIGHT,_PLAYER_SHOOT_MASKS_LEFT = [], [],[],[]
_PLAYER_SHOOT_BULLETS = []
_PLAYER_DEAD_SPRITES, _PLAYER_DEAD_LEFT_SPRITES = [], []


#sound effects of player
pygame.mixer.init()
player_run_sound = pygame.mixer.Sound(Playerrun_music)
player_run_sound.set_volume(1)
run_channel = pygame.mixer.Channel(1) 


player_shoot_sound = pygame.mixer.Sound(Playershoot_music)
player_shoot_sound.set_volume(0.5)
shoot_channel = pygame.mixer.Channel(2)

def stop_all_player_sounds():
    if run_channel.get_busy():
        run_channel.stop()
    if shoot_channel.get_busy():
        shoot_channel.stop()


def initialize_player_assets():
    global _PLAYER_RUN_SPRITES, _PLAYER_RUN_LEFT_SPRITES,_PLAYER_RUN_MASKS_RIGHT,_PLAYER_RUN_MASKS_LEFT, _PLAYER_IDLE_SPRITES, _PLAYER_IDLE_LEFT_SPRITES, \
           _PLAYER_IDLE_MASKS_RIGHT,_PLAYER_IDLE_MASKS_LEFT,_PLAYER_SHOOT_POSITION, _PLAYER_SHOOT_BULLETS, _PLAYER_SHOOT_POSITION_LEFT,_PLAYER_SHOOT_MASKS_RIGHT, _PLAYER_SHOOT_MASKS_LEFT, \
           _PLAYER_DEAD_SPRITES, _PLAYER_DEAD_LEFT_SPRITES
    
    # Load Run Sprites
    run_paths = [run1, run2, run3, run4, run5, run6, run7, run8]
    _PLAYER_RUN_SPRITES = [pygame.transform.scale(pygame.image.load(p).convert_alpha(), (PLAYER_WIDTH, PLAYER_HEIGHT)) for p in run_paths]
    _PLAYER_RUN_LEFT_SPRITES = [pygame.transform.flip(s, True, False) for s in _PLAYER_RUN_SPRITES]
    _PLAYER_RUN_MASKS_RIGHT = [pygame.mask.from_surface(img) for img in _PLAYER_RUN_SPRITES]
    _PLAYER_RUN_MASKS_LEFT = [pygame.mask.from_surface(img) for img in _PLAYER_RUN_LEFT_SPRITES]


    # Load Idle Sprites
    idle_paths = [idle1, idle2, idle3, idle4, idle5, idle6, idle7, idle8, idle9, idle10]
    _PLAYER_IDLE_SPRITES = [pygame.transform.scale(pygame.image.load(p).convert_alpha(), (PLAYER_WIDTH, PLAYER_HEIGHT)) for p in idle_paths]
    _PLAYER_IDLE_LEFT_SPRITES = [pygame.transform.flip(s, True, False) for s in _PLAYER_IDLE_SPRITES]
    _PLAYER_IDLE_MASKS_RIGHT = [pygame.mask.from_surface(img) for img in _PLAYER_IDLE_SPRITES]
    _PLAYER_IDLE_MASKS_LEFT = [pygame.mask.from_surface(img) for img in _PLAYER_IDLE_LEFT_SPRITES]


    # Load Shoot Sprites
    shoot_paths = [shoot_pos1, shoot_pos2, shoot_pos3, shoot_pos4]
    _PLAYER_SHOOT_POSITION = [pygame.transform.scale(pygame.image.load(p).convert_alpha(), (PLAYER_WIDTH, PLAYER_HEIGHT)) for p in shoot_paths]
    _PLAYER_SHOOT_POSITION_LEFT = [pygame.transform.flip(s, True, False) for s in _PLAYER_SHOOT_POSITION]
    _PLAYER_SHOOT_MASKS_RIGHT = [pygame.mask.from_surface(img) for img in _PLAYER_SHOOT_POSITION]
    _PLAYER_SHOOT_MASKS_LEFT = [pygame.mask.from_surface(img) for img in _PLAYER_SHOOT_POSITION_LEFT]


    # Load Bullet Sprites
    bullet_paths = [bullet1, bullet2, bullet3, bullet4, bullet5]
    _PLAYER_SHOOT_BULLETS = [pygame.transform.scale(pygame.image.load(p).convert_alpha(), (25, 20)) for p in bullet_paths]

    # Load Dead Sprites
    dead_paths = [player_dead1, player_dead2, player_dead3, player_dead4, player_dead5, player_dead6]
    _PLAYER_DEAD_SPRITES = [pygame.transform.scale(pygame.image.load(p).convert_alpha(), (PLAYER_WIDTH, PLAYER_HEIGHT)) for p in dead_paths]
    _PLAYER_DEAD_LEFT_SPRITES = [pygame.transform.flip(s, True, False) for s in _PLAYER_DEAD_SPRITES]

# Create class for player
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, path_tile, bullet_group: Group, health_bar_ref, immunity_bar_ref):
        super().__init__()

        self.idle_right_sprites = _PLAYER_IDLE_SPRITES
        self.idle_left_sprites = _PLAYER_IDLE_LEFT_SPRITES
        self.idle_right_masks = _PLAYER_IDLE_MASKS_RIGHT
        self.idle_left_masks = _PLAYER_IDLE_MASKS_LEFT

        self.move_right_sprites = _PLAYER_RUN_SPRITES
        self.move_left_sprites = _PLAYER_RUN_LEFT_SPRITES
        self.move_right_masks = _PLAYER_RUN_MASKS_RIGHT
        self.move_left_masks = _PLAYER_RUN_MASKS_LEFT

        self.shoot_right_sprites = _PLAYER_SHOOT_POSITION
        self.shoot_left_sprites = _PLAYER_SHOOT_POSITION_LEFT
        self.shoot_right_masks = _PLAYER_SHOOT_MASKS_RIGHT
        self.shoot_left_masks = _PLAYER_SHOOT_MASKS_LEFT

        self.dead_right_sprites = _PLAYER_DEAD_SPRITES
        self.dead_left_sprites = _PLAYER_DEAD_LEFT_SPRITES

        self.image = self.idle_right_sprites[0]

        self.rect = self.image.get_rect(midbottom=(x, y))
        self.position = vector(x, y) 
        self.velocity = vector(0, 0)
        self.acceleration = vector(0, 0)

        # Physics constants
        self.horizontal_acc = HORIZANTAL_ACC
        self.horizontal_friction = HORIZANTAL_FRICTION
        self.vertical_acc = VERTICAL_ACC
        self.vertical_jump_speed = VERTICAL_JUMP_SPEED
        self.max_horizontal_speed = MAX_HORIZANTAL_SPEED
        self.terminal_velocity = TERM_VELOCITY

        self.facing_right = True
        self.last_facing_right = True # Initialize last_facing_right to ensure consistency
        self.on_ground = True
        self.is_shooting = False
        self.shoot_cooldown = 0
        self.shoot_animation_speed = SHOOTING_SPEED
        self.bullet_group = bullet_group

        self.health_bar = health_bar_ref
        self.immunity_bar = immunity_bar_ref

        self.damage_cooldown = 0
        self.max_damage_cooldown = 90
        self.lava_damage_cooldown = 0

        self.is_dying = False
        self.death_animation_finished = False

        self.current_sprite = 0
        self.current_state = 'idle'

        self.path_tile = path_tile

        self.mask = pygame.mask.from_surface(self.image)

    def handle_event(self, event):
        pass

    def Jump(self):
        if not self.is_dying and self.on_ground and self.immunity_bar.immune >= JUMP_IMMUNITY_COST:
            self.velocity.y = -self.vertical_jump_speed
            self.on_ground = False
            self.immunity_bar.reduce_immunity(JUMP_IMMUNITY_COST)

    def shoot(self):
        if not _PLAYER_SHOOT_BULLETS:
            return

        if not self.is_dying and self.shoot_cooldown <= 0 and self.immunity_bar.immune >= BULLET_IMMUNITY_COST:
            self.is_shooting = True
            self.current_sprite = 0
            self.shoot_cooldown = 30
            self.immunity_bar.reduce_immunity(BULLET_IMMUNITY_COST)

            bullet_start_x = self.rect.centerx + (30 if self.facing_right else -30)
            bullet_start_y = self.rect.centery - 10
            new_bullet = Bullet(bullet_start_x, bullet_start_y, self.facing_right, self.path_tile)
            self.bullet_group.add(new_bullet)

            if shoot_channel.get_busy():
                shoot_channel.stop()
            shoot_channel.play(player_shoot_sound)

    def take_damage(self, amount, damage_type='melee'):
        if self.is_dying:
            return

        applied = False
        if damage_type == 'lava':
            if self.lava_damage_cooldown <= 0:
                # reduce HP
                new_hp = max(0, self.health_bar.hp - amount)
                self.health_bar.hp = new_hp
                self.lava_damage_cooldown = MAX_LAVA_DAMAGE_COOLDOWN
                applied = True
        else:
            if self.damage_cooldown <= 0:
                new_hp = max(0, self.health_bar.hp - amount)
                self.health_bar.hp = new_hp
                self.damage_cooldown = self.max_damage_cooldown
                applied = True

        # If HP reached zero then trigger dying
        if self.health_bar.hp <= 0 and not self.is_dying:
            self.is_dying = True
            self.current_sprite = 0
            self.velocity = vector(0, 0)
            self.acceleration = vector(0, 0)
            # ensure HP is exactly 0
            self.health_bar.hp = 0

    def update(self):
        # Update UI bars
        self.health_bar.update()
        self.immunity_bar.update()

        if self.is_dying:
            self.set_animation_state('dead')
            self.animate(self.dead_right_sprites, self.dead_left_sprites, 0.15)
            return

        # Immunity regeneration and cooldown updates
        self.immunity_bar.restore_immunity(IMMUNITY_REGEN_RATE)
        self.shoot_cooldown = max(0, self.shoot_cooldown - 1)
        self.damage_cooldown = max(0, self.damage_cooldown - 1)
        self.lava_damage_cooldown = max(0, self.lava_damage_cooldown - 1)

        if not self.on_ground:
            self.acceleration = vector(0, self.vertical_acc)
        else:
            self.acceleration = vector(0, 0)
        
        # --- Movement Handling ---

        # Read joystick values
        joy2_x = get_joystick_2_x()    #left/right
        joy1_y = get_joystick_1_y()   #jump/shoot

        # Thresholds
        THRESHOLD_LEFT = 250
        THRESHOLD_RIGHT = 750
        JUMP_THRESHOLD = 850
        SHOOT_THRESHOLD = 200

        moving_horizontally = False
        self.acceleration.x = 0 

        # Joystick horizontal
        if joy2_x < THRESHOLD_LEFT:
            self.facing_right = False
            self.acceleration.x = -self.horizontal_acc
            moving_horizontally = True
        elif joy2_x > THRESHOLD_RIGHT:
            self.facing_right = True
            self.acceleration.x = self.horizontal_acc
            moving_horizontally = True

        # Joystick jump
        if joy1_y > JUMP_THRESHOLD:
            self.Jump()

        if joy1_y < SHOOT_THRESHOLD:
            self.shoot()


        # Keyboard input
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:
            self.facing_right = False
            self.acceleration.x = -self.horizontal_acc
            moving_horizontally = True
        elif keys[pygame.K_RIGHT]:
            self.facing_right = True
            self.acceleration.x = self.horizontal_acc
            moving_horizontally = True

        if keys[pygame.K_f] and self.shoot_cooldown <= 0:
            self.shoot()

        if not moving_horizontally:
            self.facing_right = self.last_facing_right
        if moving_horizontally:
            self.last_facing_right = self.facing_right

        self.acceleration.x -= self.velocity.x * self.horizontal_friction

        self.velocity += self.acceleration
        self.velocity.x = max(-self.max_horizontal_speed, min(self.velocity.x, self.max_horizontal_speed))
        self.velocity.y = min(self.velocity.y, self.terminal_velocity)

        self.position.x += self.velocity.x

        if self.position.x < 0:
            self.position.x = 0
            self.velocity.x = 0  
        elif self.position.x + self.rect.width > window_width:
            self.position.x = window_width - self.rect.width
            self.velocity.x = 0

        self.rect.x = int(round(self.position.x))
        self.check_horizontal_collisions()  


        self.position.y += self.velocity.y

        self.rect.y = int(round(self.position.y))
        self.check_vertical_collisions()

        # Jump input
        if keys[pygame.K_SPACE] or keys[pygame.K_UP]:
            self.Jump()

        # Reset shooting flag after cooldown
        if self.shoot_cooldown <= 0:
            self.is_shooting = False

        # Determine current animation state
        if self.is_shooting:
            self.set_animation_state('shoot')
        elif not self.on_ground:
            self.set_animation_state('jump')
        elif moving_horizontally:
            self.set_animation_state('run')
        else:
            self.set_animation_state('idle')

        if moving_horizontally and not self.is_dying:
            if not run_channel.get_busy(): 
                run_channel.play(player_run_sound, loops=-1)
        else:
            run_channel.stop()

        # Animate sprite based on current state
        self.play_animation()

        # lava tiles and apply damage
        self.check_lava_contact()

    def set_animation_state(self, new_state):
        if self.current_state != new_state:
            self.current_state = new_state
            self.current_sprite = 0

    def play_animation(self):
        anim_speeds = {
            'idle': 0.05,
            'run': 0.2,
            'jump': 0.1,
            'shoot': self.shoot_animation_speed,
            'dead': 0.15
        }

        sprite_lists = {
            'idle': (self.idle_right_sprites, self.idle_left_sprites),
            'run': (self.move_right_sprites, self.move_left_sprites),
            'jump': (self.move_right_sprites, self.move_left_sprites),
            'shoot': (self.shoot_right_sprites, self.shoot_left_sprites),
            'dead': (self.dead_right_sprites, self.dead_left_sprites),
        }

        right_list, left_list = sprite_lists.get(self.current_state, (self.idle_right_sprites, self.idle_left_sprites))
        speed = anim_speeds.get(self.current_state, 0.1)
        self.animate(right_list, left_list, speed)

    def animate(self, right_list, left_list, speed):
            sprites = right_list if self.facing_right else left_list
            if not sprites:
                return

            # Preserve the exact midbottom position. This is the crucial anchor point 
            # (where the feet meet the ground) that should not move when the image changes.
            old_midbottom = self.rect.midbottom 

            # Update sprite index
            self.current_sprite += speed
            i = int(self.current_sprite)

            if i >= len(sprites):
                if self.is_dying:
                    i = len(sprites) - 1
                    self.death_animation_finished = True
                else:
                    self.current_sprite = 0
                    i = 0

            # Update image to the new frame
            self.image = sprites[i]

            # Recreate mask for pixel-perfect collisions
            self.mask = pygame.mask.from_surface(self.image)

            # Re-set the rect's position using the saved midbottom value.
            # This prevents the sprite from 'jumping' or 'shaking' as different-sized frames load.
            self.rect = self.image.get_rect(midbottom=old_midbottom)

    def check_horizontal_collisions(self):
        collided_tiles = pygame.sprite.spritecollide(self, main_tile_group, False, pygame.sprite.collide_mask)
        for tile in collided_tiles:
            if tile.tile_type not in [0, 7]:
                if self.velocity.x > 0:  
                    self.rect.right = tile.rect.left
                    self.position.x = self.rect.x 
                elif self.velocity.x < 0: 
                    self.rect.left = tile.rect.right
                    self.position.x = self.rect.x 
                self.velocity.x = 0

    def check_vertical_collisions(self):

        self.on_ground = False
        collided_tiles = pygame.sprite.spritecollide(self, main_tile_group, False, pygame.sprite.collide_mask)

        resolved_y = False

        for tile in collided_tiles:
            if tile.tile_type == 0:
                continue

            # Fall onto a tile
            if self.velocity.y >= 0 and self.rect.bottom > tile.rect.top >= self.rect.top:
                self.rect.bottom = tile.rect.top
                self.position.y = self.rect.y
                self.velocity.y = 0
                self.on_ground = True
                resolved_y = True
                break 

            # Jump into a tile
            elif self.velocity.y < 0 and self.rect.top < tile.rect.bottom <= self.rect.bottom:
                self.rect.top = tile.rect.bottom
                self.position.y = self.rect.y
                self.velocity.y = 0
                resolved_y = True
                break 

        if not resolved_y:
            self.position.y = self.rect.y

    def check_lava_contact(self):
        if self.lava_damage_cooldown > 0:
            return

        temp_rect = self.rect

        for tile in main_tile_group:
            if tile.tile_type == 7 and temp_rect.colliderect(tile.rect):
                self.take_damage(LAVA_DAMAGE_AMOUNT, damage_type='lava')
                break

    def reset_position(self, x, y):
        self.is_dying = False
        self.death_animation_finished = False
        self.position = vector(x, y)
        self.rect = self.image.get_rect(midbottom=self.position) 
        self.velocity = vector(0, 0)
        self.acceleration = vector(0, 0)
        self.on_ground = True
        self.facing_right = True
        self.health_bar.hp = self.health_bar.max_hp
        self.immunity_bar.immune = self.immunity_bar.max_immune
        self.current_sprite = 0
        self.current_state = 'idle'
        self.image = self.idle_right_sprites[0]
        self.mask = pygame.mask.from_surface(self.image)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction_right, collision_group: Group):
        super().__init__()
        self.bullet_sprites = _PLAYER_SHOOT_BULLETS
        if not self.bullet_sprites:
            self.kill()
            return

        self.current_sprite = 0
        self.animation_speed = 0.5
        self.image = self.bullet_sprites[0]
        self.rect = self.image.get_rect(center=(x, y)) 
        self.position = vector(x, y) 
        self.speed = BULLET_SPEED
        self.direction = 1 if direction_right else -1
        self.range = 500 
        self.traveled = 0
        self.collision_group = collision_group 

    def update(self):
        # Animate bullet
        self.current_sprite = (self.current_sprite + self.animation_speed) % len(self.bullet_sprites)
        self.image = self.bullet_sprites[int(self.current_sprite)]
        if self.direction == -1:
            self.image = pygame.transform.flip(self.image, True, False) 
        self.mask = pygame.mask.from_surface(self.image)

        # Move bullet
        move_dist = self.speed
        self.position.x += move_dist * self.direction
        self.rect.centerx = int(self.position.x) 
        self.traveled += move_dist

        # Check range
        if self.traveled > self.range:
            self.kill() 
            return

        # Check collision with solid tiles
        collided_tiles = pygame.sprite.spritecollide(self, self.collision_group, False, pygame.sprite.collide_rect)
        for tile in collided_tiles:
            if tile.tile_type not in [0, 7]:
                self.kill()
                break