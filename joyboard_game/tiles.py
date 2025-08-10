# tiles.py
# Importing needed files
import warnings
warnings.filterwarnings("ignore", category=UserWarning)
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"
import pygame
from settings import *
from tile_map import *

# Global dictionary
_PRELOADED_TILE_IMAGES = {}

def initialize_tile_assets():
    global _PRELOADED_TILE_IMAGES
    _PRELOADED_TILE_IMAGES = {
        1: pygame.transform.scale(pygame.image.load(tile1_path).convert_alpha(), (40, 40)),
        2: pygame.transform.scale(pygame.image.load(tile2_path).convert_alpha(), (40, 40)),
        3: pygame.transform.scale(pygame.image.load(tile3_path).convert_alpha(), (40, 40)),
        4: pygame.transform.scale(pygame.image.load(tile4_path).convert_alpha(), (40, 40)),
        5: pygame.transform.scale(pygame.image.load(tile5_path).convert_alpha(), (40, 40)),
        6: pygame.transform.scale(pygame.image.load(tile_water_path).convert_alpha(), (40, 40)),
        7: pygame.transform.scale(pygame.image.load(tile_lava_path).convert_alpha(), (40, 40)),
    }

# Create tile class
class Tile(pygame.sprite.Sprite):
    def __init__(self, image, x, y, tile_type):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(topleft=(x, y))
        self.tile_type = tile_type
        self.mask = pygame.mask.from_surface(self.image)

# Group for all tiles
main_tile_group = pygame.sprite.Group()

# Dictionary to store level maps
_LEVEL_MAPS = {}

def manage_level_map(level_num):
    if level_num not in _LEVEL_MAPS:
        map_data = []
        if level_num == 0: # Homepage/Start Screen
            map_data = [[0 for _ in range(window_width // TILE_SIZE)] for _ in range(window_height // TILE_SIZE)]
        elif level_num == 1:
            map_data = tile_map_1 
        elif level_num == 2:
            map_data = tile_map_2 
        elif level_num == 3:
            map_data = tile_map_3 
        elif level_num == 4:
            map_data = tile_map_4 
        elif level_num == 5:
            map_data = tile_map_5
        _LEVEL_MAPS[level_num] = map_data
    return _LEVEL_MAPS.get(level_num, [])


def fill_map(level_num):
    main_tile_group.empty() # Clearing previous tiles
    level_data = manage_level_map(level_num)

    for row_index, row in enumerate(level_data):
        for col_index, tile_type in enumerate(row):
            if tile_type != 0: # 0 represents empty space / air
                image = _PRELOADED_TILE_IMAGES.get(tile_type)
                if image:
                    x = col_index * TILE_SIZE
                    y = row_index * TILE_SIZE
                    main_tile_group.add(Tile(image, x, y, tile_type))
                else:
                    print(f"Error: No image found for tile type {tile_type}")

def find_player_spawn_point(level_data, player_height):
    if not level_data:
        return window_width / 2, window_height / 2

    # Try to find a spawn point near the horizontal center of the map
    center_col = len(level_data[0]) // 2

    for row_index in range(len(level_data) - 1, -1, -1): # Iterate from bottom row upwards
        tile_type = level_data[row_index][center_col]
        # Check for solid tiles
        if tile_type in [1, 2, 3, 4, 5, 6, 7]: 
            spawn_x = center_col * TILE_SIZE + (TILE_SIZE / 2) # Center horizontally on the tile
            spawn_y = row_index * TILE_SIZE 
            
            spawn_x_min = player_height / 2 # A buffer from the left edge
            spawn_x_max = window_width - player_height / 2 # A buffer from the right edge
            spawn_x = max(spawn_x_min, min(spawn_x, spawn_x_max))

            return spawn_x, spawn_y
    return window_width / 2, window_height / 2