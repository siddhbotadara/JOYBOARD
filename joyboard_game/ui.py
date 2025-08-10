# ui.py
# Import needed files
import warnings
warnings.filterwarnings("ignore", category=UserWarning)
import math, time
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"
import pygame
from settings import *
from input_module import get_volume_trans
from communication import first_data_received
from player import stop_all_player_sounds

# Global dictionaries/variables to store preloaded/pre-rendered assets
_PRELOADED_BACKGROUNDS = {}
_TITLE_TEXT_BASE = None
_START_TEXT_BASE_1 = None
_START_TEXT_BASE_2 = None
_SOUND_TEXT_BASE_1 = None
_SOUND_TEXT_BASE_2 = None
_STRT_IMG_PRELOADED = None
_SOUND_IMG_PRELOADED = None
_NOSOUND_IMG_PRELOADED = None
_TRANSITION_FONT = None
_GAME_OVER_FONT = None
_RESTART_FONT = None
_GAME_WON_FONT = None
_FINAL_TIME_FONT = None 
_PAUSE_FONT = None 
_PAUSE_INSTRUCTION_FONT = None

is_muted = False

# Sound effects
pygame.mixer.init()
game_over_sound = pygame.mixer.Sound(Gameover_music)
game_won_sound = pygame.mixer.Sound(Gamewon_music)
level_transition_sound = pygame.mixer.Sound(Leveltransition_music)

_game_over_played = False
_game_won_played = False


def initialize_ui_assets():
    global _PRELOADED_BACKGROUNDS, _TITLE_TEXT_BASE, _START_TEXT_BASE_1,_START_TEXT_BASE_2, _SOUND_TEXT_BASE_1,_SOUND_TEXT_BASE_2, \
           _STRT_IMG_PRELOADED, _SOUND_IMG_PRELOADED, _NOSOUND_IMG_PRELOADED, _TRANSITION_FONT, \
           _GAME_OVER_FONT, _RESTART_FONT, _GAME_WON_FONT, _FINAL_TIME_FONT, \
           _PAUSE_FONT, _PAUSE_INSTRUCTION_FONT

    # Pre-loading background images
    _PRELOADED_BACKGROUNDS = {
        0: pygame.image.load(home_page_image_path).convert(),
        1: pygame.image.load(level1_path).convert(),
        2: pygame.image.load(level2_path).convert(),
        3: pygame.image.load(level3_path).convert(),
        4: pygame.image.load(level4_path).convert(),
        5: pygame.image.load(level5_path).convert(),
    }

    # Pre-render text
    pygame.font.init()
    title_font = pygame.font.Font(home_page_font_path, 130)
    _TITLE_TEXT_BASE = title_font.render("JoyBoard", True, (255, 255, 255), None)

    start_font_1 = pygame.font.Font(home_page_font_path, 35)
    _START_TEXT_BASE_1 = start_font_1.render("PRESS 'Enter'", True, "#FFD966", None)

    start_font_2 = pygame.font.Font(home_page_font_path, 35)
    _START_TEXT_BASE_2 = start_font_2.render("PULL Right Toggle", True, "#FFD966", None)

    sound_font_1 = pygame.font.Font(home_page_font_path, 25)
    _SOUND_TEXT_BASE_1 = sound_font_1.render("PRESS 'm'", True, "#FFD966", None)

    sound_font_2 = pygame.font.Font(home_page_font_path, 25)
    _SOUND_TEXT_BASE_2 = sound_font_2.render("vary Pot", True, "#FFD966", None)

    _TRANSITION_FONT = pygame.font.Font(home_page_font_path, 80)
    _GAME_OVER_FONT = pygame.font.Font(home_page_font_path, 100)
    _RESTART_FONT = pygame.font.Font(home_page_font_path, 40)
    _GAME_WON_FONT = pygame.font.Font(home_page_font_path, 100) 
    _FINAL_TIME_FONT = pygame.font.Font(home_page_font_path, 50)
    _PAUSE_FONT = pygame.font.Font(home_page_font_path, 80)
    _PAUSE_INSTRUCTION_FONT = pygame.font.Font(home_page_font_path, 30)

    # Pre-load icons
    _STRT_IMG_PRELOADED = pygame.transform.scale(pygame.image.load(home_page_start_path).convert_alpha(), (400,400))
    _SOUND_IMG_PRELOADED = pygame.transform.scale(pygame.image.load(home_page_sound_path).convert_alpha(), (100,100))
    _NOSOUND_IMG_PRELOADED = pygame.transform.scale(pygame.image.load(home_page_nosound_path).convert_alpha(), (100,100))


# Background based on level
def get_background(current_level):
    bg_image = _PRELOADED_BACKGROUNDS.get(current_level)
    if bg_image is None:
        return pygame.Surface((window_width, window_height)), pygame.Rect(0,0,window_width,window_height)
    bg_image_rect = bg_image.get_rect(topleft=(0, 0))
    return bg_image, bg_image_rect

# Homepage - Music
def Homepage_music():
    global is_muted
    if not is_muted:
        pygame.mixer.init()
        pygame.mixer.music.load(home_page_music_path)

        # Wait until first Arduino input received
        start_time = time.time()
        while not first_data_received and (time.time() - start_time < 2):
            time.sleep(0.05)

        pygame.mixer.music.set_volume(get_volume_trans())
        pygame.mixer.music.play(-1)

# Level Background Music
def level_background_music():
    global is_muted
    if not is_muted:
        pygame.mixer.music.load(bg_sound)
        pygame.mixer.music.set_volume(get_volume_trans())
        pygame.mixer.music.play(-1)


# Homepage - Text
def Homepage_text(width,height):
    if _TITLE_TEXT_BASE is None or _START_TEXT_BASE_1 is None or _SOUND_TEXT_BASE_1 is None:
        raise RuntimeError("Error loading UI text assets.")

    # Apply flicker effect
    start_text_flickered_1 = flicker_surface(_START_TEXT_BASE_1, 3)
    start_text_flickered_2 = flicker_surface(_START_TEXT_BASE_2, 3)
    sound_text_flickered_1 = flicker_surface(_SOUND_TEXT_BASE_1, 3)
    sound_text_flickered_2 = flicker_surface(_SOUND_TEXT_BASE_2, 3)

    title_text_rect = _TITLE_TEXT_BASE.get_rect(center=(width / 2, height - 615))
    start_text_rect_1 = start_text_flickered_1.get_rect(center=(width / 2, height / 2 + 155))
    start_text_rect_2 = start_text_flickered_2.get_rect(center=(width / 2, height / 2 + 200))
    sound_text_rect_1 = sound_text_flickered_1.get_rect(center=(width - 58, 110))
    sound_text_rect_2 = sound_text_flickered_2.get_rect(center=(width - 58, 140))

    return _TITLE_TEXT_BASE, title_text_rect, start_text_flickered_1,start_text_flickered_2, start_text_rect_1,start_text_rect_2, sound_text_flickered_1,sound_text_flickered_2, sound_text_rect_1, sound_text_rect_2

# Homepage - Icons
def Homepage_icons(width,height):
    if _STRT_IMG_PRELOADED is None or _SOUND_IMG_PRELOADED is None or _NOSOUND_IMG_PRELOADED is None:
        raise RuntimeError("Error loading UI icon assets.")

    # Apply flicker
    start_image_flickered = flicker_surface(_STRT_IMG_PRELOADED, 0)

    start_image_rect = start_image_flickered.get_rect(center=(width/2,height/2))
    sound_image_rect = _SOUND_IMG_PRELOADED.get_rect(topright=(width,0))
    nosound_image_rect = _NOSOUND_IMG_PRELOADED.get_rect(topright=(width,0))

    return start_image_flickered, start_image_rect, _SOUND_IMG_PRELOADED, sound_image_rect, _NOSOUND_IMG_PRELOADED, nosound_image_rect

# Animation For Image/Text
def flicker_surface(surface, speed, min_alpha=100, max_alpha=255):
    t = time.time()
    alpha = int((max_alpha - min_alpha)/2 * math.sin(t * speed) + (min_alpha + max_alpha)/2)
    flickered = surface.copy()
    flickered.set_alpha(alpha)
    return flickered

# Creating an oqaque screen, stating level details and time for get ready 3 seconds
def transition_level(screen, level_number, duration_frames=180):
    if _TRANSITION_FONT is None:
        raise RuntimeError("Error loading Transition font.")
    
    stop_all_player_sounds()

    # Sound effect when switching levels
    level_transition_sound.play(loops=2)

    # Creating a semi-transparent black overlay
    overlay = pygame.Surface((window_width, window_height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 128)) # 128 = 50% Transparency

    # Render level text
    if level_number == 0:
        level_text_str = "Home Base"
    elif level_number == 5:
        level_text_str = "Final Level"
    else:
        level_text_str = f"Level {level_number}"
    
    level_text_surface = _TRANSITION_FONT.render(level_text_str, True, (255, 255, 255))
    level_text_rect = level_text_surface.get_rect(center=(window_width / 2, window_height / 2))

    # Get ready text
    get_ready_font = pygame.font.Font(home_page_font_path, 40)
    get_ready_text_surface = get_ready_font.render("GET READY!", True, (255, 255, 0))
    get_ready_text_rect = get_ready_text_surface.get_rect(center=(window_width / 2, window_height / 2 + 80))

    # Animation loop for transition
    for frame in range(duration_frames):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        # Draw the overlay
        screen.blit(overlay, (0, 0))
        
        # Draw the text
        screen.blit(level_text_surface, level_text_rect)
        
        # Make "GET READY!" text flicker
        flickered_ready_text = flicker_surface(get_ready_text_surface, 5)
        screen.blit(flickered_ready_text, get_ready_text_rect)

        pygame.display.flip()
        pygame.time.Clock().tick(fps)
    
    level_transition_sound.stop()

# Create class for health bar
class player_health_bar():
    def __init__(self,x,y,width,height,max_hp):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.max_hp = max_hp
        self.hp = max_hp

        self.displayed_hp = float(self.hp)
        self.lerp_speed = 0.08

        self.is_flashing = False
        self.flash_timer = 0
        self.flash_duration = 10
        self.flash_color = (255, 255, 255, 150) 

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp < 0:
            self.hp = 0 # Ensure health doesn't go below zero
            current_game_state = GAME_STATE_GAME_OVER
        
        self.is_flashing = True
        self.flash_timer = self.flash_duration

    def heal(self, amount):
        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp # Ensure health doesn't exceed max_hp

    def get_health_color(self, current_ratio):
        GREEN = (0, 255, 0)
        YELLOW = (255, 255, 0)
        RED = (255, 0, 0)

        if current_ratio > 0.5:
            interp_factor = (current_ratio - 0.5) * 2
            return (
                int(YELLOW[0] + (GREEN[0] - YELLOW[0]) * interp_factor),
                int(YELLOW[1] + (GREEN[1] - YELLOW[1]) * interp_factor),
                int(YELLOW[2] + (GREEN[2] - YELLOW[2]) * interp_factor)
            )
        else:
            interp_factor = current_ratio * 2
            return (
                int(RED[0] + (YELLOW[0] - RED[0]) * interp_factor),
                int(RED[1] + (YELLOW[1] - RED[1]) * interp_factor),
                int(RED[2] + (YELLOW[2] - RED[2]) * interp_factor)
            )

    def draw(self, surface):
        EMPTY_COLOR = (50, 50, 50)  
        BORDER_COLOR = (0, 0, 0) 
        BORDER_THICKNESS = 2     

        # Calculate ratios for drawing
        current_fill_ratio = self.displayed_hp / self.max_hp

        # Draw the background of the health bar
        pygame.draw.rect(surface, EMPTY_COLOR, (self.x, self.y, self.width, self.height))

        # Draw the current health portion with dynamic color
        current_health_color = self.get_health_color(current_fill_ratio)
        pygame.draw.rect(surface, current_health_color, (self.x, self.y, self.width * current_fill_ratio, self.height))

        # Draw the border around the health bar
        border_rect = (
            self.x - BORDER_THICKNESS,
            self.y - BORDER_THICKNESS,
            self.width + (2 * BORDER_THICKNESS),
            self.height + (2 * BORDER_THICKNESS)
        )
        pygame.draw.rect(surface, BORDER_COLOR, border_rect, BORDER_THICKNESS)

        if self.is_flashing:
            flash_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            flash_surface.fill(self.flash_color)
            surface.blit(flash_surface, (self.x, self.y))

    def update(self):
        if abs(self.displayed_hp - self.hp) > 0.1:
            self.displayed_hp = self.displayed_hp + (self.hp - self.displayed_hp) * self.lerp_speed
        else:
            self.displayed_hp = float(self.hp)

        if self.displayed_hp < 0:
            self.displayed_hp = 0
        elif self.displayed_hp > self.max_hp:
            self.displayed_hp = self.max_hp
    
        if self.is_flashing:
            self.flash_timer -= 1
            if self.flash_timer <= 0:
                self.is_flashing = False

# Create class immunity bar for the player
class player_immunity_bar():
    def __init__(self,x,y,width,height,max_immune):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.max_immune = max_immune
        self.immune = max_immune

        self.displayed_immune = float(self.immune)
        self.lerp_speed = 0.08

        self.is_flashing = False
        self.flash_timer = 0
        self.flash_duration = 10
        self.flash_color = (255, 255, 255, 150)


    def reduce_immunity(self, amount):
        self.immune -= amount
        if self.immune < 0:
            self.immune = 0
        
        self.is_flashing = True
        self.flash_timer = self.flash_duration

    def restore_immunity(self, amount):
        self.immune += amount
        if self.immune > self.max_immune:
            self.immune = self.max_immune

    def get_immunity_color(self, current_ratio):
        BLUE = (0, 191, 255) 
        LIGHT_BLUE = (173, 216, 230) 
        ORANGE = (255, 165, 0) 

        if current_ratio > 0.5:
            interp_factor = (current_ratio - 0.5) * 2
            return (
                int(LIGHT_BLUE[0] + (BLUE[0] - LIGHT_BLUE[0]) * interp_factor),
                int(LIGHT_BLUE[1] + (BLUE[1] - LIGHT_BLUE[1]) * interp_factor),
                int(LIGHT_BLUE[2] + (BLUE[2] - LIGHT_BLUE[2]) * interp_factor)
            )
        else:
            interp_factor = current_ratio * 2
            return (
                int(ORANGE[0] + (LIGHT_BLUE[0] - ORANGE[0]) * interp_factor),
                int(ORANGE[1] + (LIGHT_BLUE[1] - ORANGE[1]) * interp_factor),
                int(ORANGE[2] + (LIGHT_BLUE[2] - ORANGE[2]) * interp_factor)
            )

    def draw(self,surface):
        EMPTY_COLOR = (30, 30, 80) 
        BORDER_COLOR = (0, 0, 0)
        BORDER_THICKNESS = 2

        current_fill_ratio = self.displayed_immune / self.max_immune

        pygame.draw.rect(surface, EMPTY_COLOR, (self.x, self.y, self.width, self.height))
        
        current_immunity_color = self.get_immunity_color(current_fill_ratio)
        pygame.draw.rect(surface, current_immunity_color, (self.x, self.y, self.width * current_fill_ratio, self.height))

        border_rect = (
            self.x - BORDER_THICKNESS,
            self.y - BORDER_THICKNESS,
            self.width + (2 * BORDER_THICKNESS),
            self.height + (2 * BORDER_THICKNESS)
        )
        pygame.draw.rect(surface, BORDER_COLOR, border_rect, BORDER_THICKNESS)

        if self.is_flashing:
            flash_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            flash_surface.fill(self.flash_color)
            surface.blit(flash_surface, (self.x, self.y))

    def update(self):
        if abs(self.displayed_immune - self.immune) > 0.1:
            self.displayed_immune = self.displayed_immune + (self.immune - self.displayed_immune) * self.lerp_speed
        else:
            self.displayed_immune = float(self.immune)

        if self.displayed_immune < 0:
            self.displayed_immune = 0
        elif self.displayed_immune > self.max_immune:
            self.displayed_immune = self.max_immune

        if self.is_flashing:
            self.flash_timer -= 1
            if self.flash_timer <= 0:
                self.is_flashing = False

# Game Over display function
def game_over(surface, width, height):
    if _GAME_OVER_FONT is None or _RESTART_FONT is None:
        raise RuntimeError("Error loading Game Over fonts.")
    
    stop_all_player_sounds()

    surface.fill((0, 0, 0))  

    overlay = pygame.Surface((width, height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    
    # "GAME OVER" text
    game_over_text = _GAME_OVER_FONT.render("GAME OVER", True, (255, 0, 0))
    game_over_rect = game_over_text.get_rect(center=(width / 2, height / 2 - 50))

    # Restart instruction text
    restart_text = _RESTART_FONT.render("Press 'R'/Push Toggle Down to Restart", True, (255, 255, 255)) 
    restart_rect = restart_text.get_rect(center=(width / 2, height / 2 + 50))

    surface.blit(overlay, (0, 0))
    surface.blit(game_over_text, game_over_rect)
    surface.blit(restart_text, restart_rect)

    global _game_over_played
    
    if not _game_over_played:
        game_over_sound.play()
        _game_over_played = True


# Game Won display function
def game_won(surface, width, height, total_time):
    # Total time recalculated - subtracted transition time
    new_total_time = total_time - 20
    
    if _GAME_WON_FONT is None or _FINAL_TIME_FONT is None or _RESTART_FONT is None:
        raise RuntimeError(" Error loading Game Won fonts.")

    stop_all_player_sounds()

    surface.fill((0, 0, 0))  

    overlay = pygame.Surface((width, height), pygame.SRCALPHA)
    overlay.fill((0, 50, 0, 180))

    # "YOU WON!" text
    game_won_text = _GAME_WON_FONT.render("YOU WON!", True, (0, 255, 0)) 
    game_won_rect = game_won_text.get_rect(center=(width / 2, height / 2 - 100))
    
    # Total time text
    total_time_text_str = f"Total Time: {new_total_time:.2f}s"
    total_time_text = _FINAL_TIME_FONT.render(total_time_text_str, True, (255, 255, 0)) 
    total_time_rect = total_time_text.get_rect(center=(width / 2, height / 2))

    # Restart instruction text
    restart_text = _RESTART_FONT.render("Press 'R'/Push Toggle Down to Restart", True, (255, 255, 255))  
    restart_rect = restart_text.get_rect(center=(width / 2, height / 2 + 100))

    surface.blit(overlay, (0, 0))
    surface.blit(game_won_text, game_won_rect)
    surface.blit(total_time_text, total_time_rect)
    surface.blit(restart_text, restart_rect)

    global _game_won_played
    
    if not _game_won_played:
        game_won_sound.play()
        _game_won_played = True

# Pause screen display function
def pause_screen(surface, width, height):
    if _PAUSE_FONT is None or _PAUSE_INSTRUCTION_FONT is None:
        raise RuntimeError("Error loading Pause fonts.")

    stop_all_player_sounds()

    overlay = pygame.Surface((width, height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))

    # "PAUSED" text
    paused_text = _PAUSE_FONT.render("PAUSED", True, (255, 255, 255))
    paused_rect = paused_text.get_rect(center=(width / 2, height / 2 - 50))

    # Instructions text
    resume_text = _PAUSE_INSTRUCTION_FONT.render("Press 'ESC'/Button-1 to Resume", True, (200, 200, 200))
    resume_rect = resume_text.get_rect(center=(width / 2, height / 2 + 20))

    homepage_text = _PAUSE_INSTRUCTION_FONT.render("Press 'H'/Button-2 for Homepage", True, (200, 200, 200))
    homepage_rect = homepage_text.get_rect(center=(width / 2, height / 2 + 60))

    surface.blit(overlay, (0, 0))
    surface.blit(paused_text, paused_rect)
    surface.blit(resume_text, resume_rect)
    surface.blit(homepage_text, homepage_rect)