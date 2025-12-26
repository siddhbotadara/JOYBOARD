# Enemy.py
# Importing needed files
import warnings
warnings.filterwarnings("ignore", category=UserWarning)
import random
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"
import pygame
from pygame.sprite import Group
from settings import *
from tiles import manage_level_map, main_tile_group
from tile_map import *
import settings

enemy_group = pygame.sprite.Group() 

# Define 2D vector
vector = pygame.math.Vector2

# Global variables to store preloaded enemy sprites
_ENEMY_IDLE_SPRITES = []
_ENEMY_WALK_SPRITES = []
_ENEMY_DEAD_SPRITES = []
_ENEMY_IDLE_SPRITES_LEFT = []
_ENEMY_WALK_SPRITES_LEFT = []
_ENEMY_DEAD_SPRITES_LEFT = []

# Global variable to store enemy bullet sprites
_ENEMY_BULLET_SPRITES = []


def initialize_enemy_assets():
    global _ENEMY_IDLE_SPRITES, _ENEMY_DEAD_SPRITES, _ENEMY_WALK_SPRITES, \
           _ENEMY_IDLE_SPRITES_LEFT, _ENEMY_DEAD_SPRITES_LEFT, _ENEMY_WALK_SPRITES_LEFT, \
           _ENEMY_BULLET_SPRITES

    try:
        # Load sprites
        _ENEMY_WALK_SPRITES = [
            pygame.transform.scale(pygame.image.load(enemy_walk1).convert_alpha(), (ENEMY_WIDTH, ENEMY_HEIGHT)),
            pygame.transform.scale(pygame.image.load(enemy_walk2).convert_alpha(), (ENEMY_WIDTH, ENEMY_HEIGHT)),
            pygame.transform.scale(pygame.image.load(enemy_walk3).convert_alpha(), (ENEMY_WIDTH, ENEMY_HEIGHT)),
            pygame.transform.scale(pygame.image.load(enemy_walk4).convert_alpha(), (ENEMY_WIDTH, ENEMY_HEIGHT)),
            pygame.transform.scale(pygame.image.load(enemy_walk5).convert_alpha(), (ENEMY_WIDTH, ENEMY_HEIGHT)),
            pygame.transform.scale(pygame.image.load(enemy_walk6).convert_alpha(), (ENEMY_WIDTH, ENEMY_HEIGHT)),
            pygame.transform.scale(pygame.image.load(enemy_walk7).convert_alpha(), (ENEMY_WIDTH, ENEMY_HEIGHT)),
            pygame.transform.scale(pygame.image.load(enemy_walk8).convert_alpha(), (ENEMY_WIDTH, ENEMY_HEIGHT)),
            pygame.transform.scale(pygame.image.load(enemy_walk9).convert_alpha(), (ENEMY_WIDTH, ENEMY_HEIGHT)),
            pygame.transform.scale(pygame.image.load(enemy_walk10).convert_alpha(), (ENEMY_WIDTH, ENEMY_HEIGHT))
        ]
        _ENEMY_WALK_SPRITES_LEFT = [pygame.transform.flip(sprite, True, False) for sprite in _ENEMY_WALK_SPRITES]

        # Load idle sprites
        _ENEMY_IDLE_SPRITES = [
            pygame.transform.scale(pygame.image.load(enemy_idle1).convert_alpha(), (ENEMY_WIDTH, ENEMY_HEIGHT)),
            pygame.transform.scale(pygame.image.load(enemy_idle2).convert_alpha(), (ENEMY_WIDTH, ENEMY_HEIGHT)),
            pygame.transform.scale(pygame.image.load(enemy_idle3).convert_alpha(), (ENEMY_WIDTH, ENEMY_HEIGHT)),
            pygame.transform.scale(pygame.image.load(enemy_idle4).convert_alpha(), (ENEMY_WIDTH, ENEMY_HEIGHT)),
            pygame.transform.scale(pygame.image.load(enemy_idle5).convert_alpha(), (ENEMY_WIDTH, ENEMY_HEIGHT)),
            pygame.transform.scale(pygame.image.load(enemy_idle6).convert_alpha(), (ENEMY_WIDTH, ENEMY_HEIGHT)),
            pygame.transform.scale(pygame.image.load(enemy_idle7).convert_alpha(), (ENEMY_WIDTH, ENEMY_HEIGHT)),
            pygame.transform.scale(pygame.image.load(enemy_idle8).convert_alpha(), (ENEMY_WIDTH, ENEMY_HEIGHT)),
            pygame.transform.scale(pygame.image.load(enemy_idle9).convert_alpha(), (ENEMY_WIDTH, ENEMY_HEIGHT)),
            pygame.transform.scale(pygame.image.load(enemy_idle10).convert_alpha(), (ENEMY_WIDTH, ENEMY_HEIGHT)),
            pygame.transform.scale(pygame.image.load(enemy_idle11).convert_alpha(), (ENEMY_WIDTH, ENEMY_HEIGHT)),
            pygame.transform.scale(pygame.image.load(enemy_idle12).convert_alpha(), (ENEMY_WIDTH, ENEMY_HEIGHT)),
            pygame.transform.scale(pygame.image.load(enemy_idle13).convert_alpha(), (ENEMY_WIDTH, ENEMY_HEIGHT)),
            pygame.transform.scale(pygame.image.load(enemy_idle14).convert_alpha(), (ENEMY_WIDTH, ENEMY_HEIGHT)),
            pygame.transform.scale(pygame.image.load(enemy_idle15).convert_alpha(), (ENEMY_WIDTH, ENEMY_HEIGHT)),
        ]
        _ENEMY_IDLE_SPRITES_LEFT = [pygame.transform.flip(sprite, True, False) for sprite in _ENEMY_IDLE_SPRITES]

        # Load dead sprites
        _ENEMY_DEAD_SPRITES = [
            pygame.transform.scale(pygame.image.load(enemy_dead1).convert_alpha(), (ENEMY_WIDTH, ENEMY_HEIGHT)),
            pygame.transform.scale(pygame.image.load(enemy_dead2).convert_alpha(), (ENEMY_WIDTH, ENEMY_HEIGHT)),
            pygame.transform.scale(pygame.image.load(enemy_dead3).convert_alpha(), (ENEMY_WIDTH, ENEMY_HEIGHT)),
            pygame.transform.scale(pygame.image.load(enemy_dead4).convert_alpha(), (ENEMY_WIDTH, ENEMY_HEIGHT)),
            pygame.transform.scale(pygame.image.load(enemy_dead5).convert_alpha(), (ENEMY_WIDTH, ENEMY_HEIGHT)),
            pygame.transform.scale(pygame.image.load(enemy_dead6).convert_alpha(), (ENEMY_WIDTH, ENEMY_HEIGHT)),
            pygame.transform.scale(pygame.image.load(enemy_dead7).convert_alpha(), (ENEMY_WIDTH, ENEMY_HEIGHT)),
            pygame.transform.scale(pygame.image.load(enemy_dead8).convert_alpha(), (ENEMY_WIDTH, ENEMY_HEIGHT)),
            pygame.transform.scale(pygame.image.load(enemy_dead9).convert_alpha(), (ENEMY_WIDTH, ENEMY_HEIGHT)),
            pygame.transform.scale(pygame.image.load(enemy_dead10).convert_alpha(), (ENEMY_WIDTH, ENEMY_HEIGHT)),
            pygame.transform.scale(pygame.image.load(enemy_dead11).convert_alpha(), (ENEMY_WIDTH, ENEMY_HEIGHT)),
            # Corrected typo here: ENEDY_HEIGHT to ENEMY_HEIGHT
            pygame.transform.scale(pygame.image.load(enemy_dead12).convert_alpha(), (ENEMY_WIDTH, ENEMY_HEIGHT)), 
        ]
        _ENEMY_DEAD_SPRITES_LEFT = [pygame.transform.flip(sprite, True, False) for sprite in _ENEMY_DEAD_SPRITES]
        
        # Load enemy bullet sprites
        _ENEMY_BULLET_SPRITES = [
            pygame.transform.scale(pygame.image.load(bullet1).convert_alpha(),(25,20)),
            pygame.transform.scale(pygame.image.load(bullet2).convert_alpha(),(25,20)),
            pygame.transform.scale(pygame.image.load(bullet3).convert_alpha(),(25,20)),
            pygame.transform.scale(pygame.image.load(bullet4).convert_alpha(),(25,20)),
            pygame.transform.scale(pygame.image.load(bullet5).convert_alpha(),(25,20)),
        ]

    except Exception as e:
        print(f"Error loading enemy assets: {e}.")


# EnemyBullet class
class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, collision_group: Group):
        super().__init__()
        self.bullet_sprites = _ENEMY_BULLET_SPRITES
        self.current_sprite = 0
        self.animation_speed = 0.2

        if not self.bullet_sprites:
            raise RuntimeError("Error loading Enemy bullet sprites.")

        self.image = self.bullet_sprites[0]
        self.rect = self.image.get_rect(center=(x, y))
        self.position = vector(x, y)
        self.speed = 10
        self.direction = direction
        self.initial_x = x 
        self.range = 500
        self.collision_group = collision_group

    def update(self):
        self.current_sprite += self.animation_speed
        if self.current_sprite >= len(self.bullet_sprites):
            self.current_sprite = 0
        self.image = self.bullet_sprites[int(self.current_sprite)]

        # Flip bullet sprite if moving left
        if self.direction == -1:
            self.image = pygame.transform.flip(self.image, True, False)

        # Move the bullet
        self.position.x += self.speed * self.direction
        self.rect.centerx = int(self.position.x)

        # Check if out of range
        if abs(self.position.x - self.initial_x) > self.range:
            self.kill() # Remove bullet if out of range

        # Check for collision with tiles
        collided_tiles = pygame.sprite.spritecollide(self, self.collision_group, False, pygame.sprite.collide_mask)
        if collided_tiles:
            self.kill() # Remove bullet on collision

# Base Enemy Class
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, enemy_bullets_group: Group, player_obj, initial_health=3, is_walking=False):
        super().__init__()

        self.animation_speed = 0.20
        self.current_sprite = 0
        self.facing_right = random.choice([True, False])
        self.on_ground = False
        self.speed = 1 if is_walking else 0 
        self.gravity = 0.5
        self.vertical_momentum = 0

        self.health = initial_health
        self.is_dead = False
        self.death_animation_finished = False
        self.is_walking = is_walking

        # Shooting variables
        self.enemy_bullets_group = enemy_bullets_group
        self.player_obj = player_obj

        self.shoot_cooldown = random.randint(MIN_ENEMY_SHOOT_COOLDOWN, MAX_ENEMY_SHOOT_COOLDOWN) 
        self.shoot_range = ENEMY_SHOOT_RANGE

        # Ensure sprites are loaded before accessing them
        if not _ENEMY_IDLE_SPRITES:
            self.image = pygame.Surface((ENEMY_WIDTH, ENEMY_HEIGHT), pygame.SRCALPHA)
            self.image.fill((255, 0, 0, 128))
        else:
            self.image = _ENEMY_IDLE_SPRITES[0] 
        self.rect = self.image.get_rect(bottomleft=(x, y))

    def apply_gravity(self):
        if not self.is_dead:
            self.vertical_momentum += self.gravity
            self.rect.y += self.vertical_momentum

    def check_collisions_with_tiles(self, tile_group, horizontal_movement=True):
        if self.is_dead: return # No collision checks if dead

        # --- Horizontal Movement and Collision ---
        if horizontal_movement and self.is_walking:
            if self.facing_right:
                self.rect.x += self.speed
            else:
                self.rect.x -= self.speed

            hit_tiles_x = pygame.sprite.spritecollide(self, tile_group, False)
            for tile in hit_tiles_x:
                if tile.tile_type != 0 and tile.tile_type != 7:
                    if self.facing_right:
                        self.rect.right = tile.rect.left
                    else:
                        self.rect.left = tile.rect.right
                    self.facing_right = not self.facing_right 
                    break

        # --- Vertical Movement and Collision ---
        self.on_ground = False 

        hit_tiles_y = pygame.sprite.spritecollide(self, tile_group, False)
        for tile in hit_tiles_y:
            if tile.tile_type != 0 and tile.tile_type != 7:
                if self.vertical_momentum > 0: 
                    self.rect.bottom = tile.rect.top
                    self.on_ground = True
                elif self.vertical_momentum < 0: 
                    self.rect.top = tile.rect.bottom
                self.vertical_momentum = 0
                break 

        # Keep enemy within horizontal screen bounds and turn around if hitting edges (future)
        if horizontal_movement and self.is_walking:
            if self.rect.left < 0:
                self.rect.left = 0
                self.facing_right = True
            if self.rect.right > window_width:
                self.rect.right = window_width
                self.facing_right = False


    def animate(self, sprites_list_right, sprites_list_left):
        if self.is_dead:
            if not _ENEMY_DEAD_SPRITES:
                self.image.fill((255, 0, 0, 100))
                self.death_animation_finished = True
                return
            
            self.current_sprite += self.animation_speed
            if self.current_sprite >= len(sprites_list_right):
                self.current_sprite = len(sprites_list_right) - 1
                self.death_animation_finished = True
            
            if self.facing_right:
                self.image = _ENEMY_DEAD_SPRITES[int(self.current_sprite)]
            else:
                self.image = _ENEMY_DEAD_SPRITES_LEFT[int(self.current_sprite)]

        else: 
            if not sprites_list_right or not sprites_list_left:
                return

            self.current_sprite += self.animation_speed
            if self.current_sprite >= len(sprites_list_right):
                self.current_sprite = 0 

            if self.facing_right:
                self.image = sprites_list_right[int(self.current_sprite)]
            else:
                self.image = sprites_list_left[int(self.current_sprite)]

    def take_damage(self, amount):
        if not self.is_dead:
            self.health -= amount
            if self.health <= 0:
                self.is_dead = True
                self.vertical_momentum = 0
                self.current_sprite = 0 

    def shoot(self):
        bullet_start_x = self.rect.centerx
        bullet_start_y = self.rect.centery - 10 

        # Determine bullet direction based on enemy facing
        bullet_direction = 1 if self.facing_right else -1

        new_bullet = EnemyBullet(bullet_start_x, bullet_start_y, bullet_direction, main_tile_group)
        self.enemy_bullets_group.add(new_bullet)
        self.shoot_cooldown = random.randint(MIN_ENEMY_SHOOT_COOLDOWN, MAX_ENEMY_SHOOT_COOLDOWN)

    def update(self):
        if self.is_dead:
            self.animate(_ENEMY_DEAD_SPRITES, _ENEMY_DEAD_SPRITES_LEFT)
            if self.death_animation_finished:
                self.kill() # Remove sprite from all groups when death animation is complete
            return

        self.apply_gravity()
        self.check_collisions_with_tiles(main_tile_group, horizontal_movement=self.is_walking) 
        
        if self.is_walking:
            self.animate(_ENEMY_WALK_SPRITES, _ENEMY_WALK_SPRITES_LEFT)
        else:
            self.animate(_ENEMY_IDLE_SPRITES, _ENEMY_IDLE_SPRITES_LEFT)

        # Enemy shooting logic
        self.shoot_cooldown -= 1
        if self.on_ground and not self.is_dead:
            player_distance_x = abs(self.rect.centerx - self.player_obj.rect.centerx)
            player_distance_y = abs(self.rect.centery - self.player_obj.rect.centery)
            # Check if player is within shooting range AND cooldown allows a shot
            vertical_shoot_threshold = ENEMY_HEIGHT
            if (player_distance_x <= self.shoot_range and 
                player_distance_y <= vertical_shoot_threshold and 
                self.shoot_cooldown <= 0):
                if self.player_obj.rect.centerx < self.rect.centerx:
                    self.facing_right = False
                else:
                    self.facing_right = True
                self.shoot() 

def is_position_valid(potential_x, potential_y, existing_enemies_group, min_distance_blocks=8):
    min_pixel_distance = min_distance_blocks * TILE_SIZE

    if not _ENEMY_IDLE_SPRITES:
        temp_enemy_image = pygame.Surface((ENEMY_WIDTH, ENEMY_HEIGHT), pygame.SRCALPHA)
    else:
        temp_enemy_image = _ENEMY_IDLE_SPRITES[0]

    temp_enemy_rect = temp_enemy_image.get_rect(bottomleft=(potential_x, potential_y))

    for existing_enemy in existing_enemies_group:
        if temp_enemy_rect.colliderect(existing_enemy.rect.inflate(min_pixel_distance, min_pixel_distance)):
            return False 

    return True


def spawn_enemies_for_level(current_level, enemy_bullets_group: Group, player_obj):
    enemy_group.empty() 
    tile_map_data = manage_level_map(current_level)

    placed_enemies_temp_group = Group()

    if current_level == 0: # No enemies on home base
        return

    base_enemies_count = 6
    enemies_to_place = base_enemies_count + (current_level - 1) * 2
    if enemies_to_place < 0:
        enemies_to_place = 0

    base_enemy_health = 1
    enemy_health_for_level = base_enemy_health + (current_level - 1)
    if enemy_health_for_level < 1:
        enemy_health_for_level = 1

    valid_ground_y_coords = set()
    for r in range(len(tile_map_data)):
        for c in range(len(tile_map_data[r])):
            tile_value = tile_map_data[r][c]
            if tile_value != 0 and tile_value != 7:
                if r > 1 and tile_map_data[r-1][c] == 0 and tile_map_data[r-2][c] == 0:
                    enemy_ground_y = (r * TILE_SIZE) + TILE_SIZE
                    valid_ground_y_coords.add(enemy_ground_y)

    valid_ground_y_coords_list = sorted(list(valid_ground_y_coords)) 
    if not valid_ground_y_coords_list:
        print("Error!")
        valid_ground_y_coords_list = [window_height - TILE_SIZE] 

    # Generate initial potential spawn points for enemies
    potential_spawn_points = []
    for r in range(len(tile_map_data)):
        for c in range(len(tile_map_data[r])):
            tile_value = tile_map_data[r][c]
            if tile_value != 0 and tile_value != 7:
                if r > 1 and tile_map_data[r-1][c] == 0 and tile_map_data[r-2][c] == 0:
                    potential_spawn_points.append((c * TILE_SIZE, (r * TILE_SIZE) + TILE_SIZE))
    random.shuffle(potential_spawn_points)

    # Loop to place each desired enemy
    enemies_placed_count = 0
    attempts_per_enemy = 100 

    for enemy_idx in range(enemies_to_place):
        found_spot = False
        current_attempts_points = list(potential_spawn_points) 
        random.shuffle(current_attempts_points)

        for attempt_num in range(attempts_per_enemy):
            if not current_attempts_points:
                break

            px, py = current_attempts_points.pop(0)

            # Check spacing with already placed enemies
            current_min_distance_blocks = 3 
            if is_position_valid(px, py, placed_enemies_temp_group, min_distance_blocks=current_min_distance_blocks):
                mult = 1.0
                if hasattr(player_obj, 'health_bar') and hasattr(settings, "_DDA_ENEMY_HEALTH_MULTIPLIER"):
                    try:
                        mult = settings._DDA_ENEMY_HEALTH_MULTIPLIER
                    except Exception:
                        mult = 1.0

                # compute health to pass
                adjusted_enemy_health = max(1, int(round(enemy_health_for_level * mult)))
                temp_enemy = Enemy(px, py, enemy_bullets_group, player_obj, initial_health=adjusted_enemy_health, is_walking=False)

                temp_enemy.apply_gravity()
                temp_enemy.check_collisions_with_tiles(main_tile_group, horizontal_movement=False)

                if temp_enemy.on_ground:
                    enemy_group.add(temp_enemy)
                    placed_enemies_temp_group.add(temp_enemy)
                    enemies_placed_count += 1
                    found_spot = True
                    if (px, py) in potential_spawn_points:
                        potential_spawn_points.remove((px, py))
                    break 
                else:
                    if (px, py) in potential_spawn_points:
                        potential_spawn_points.remove((px, py))
        
        if enemies_placed_count == enemies_to_place:
            break