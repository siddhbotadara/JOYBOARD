# input.py
# Import needed files
import warnings
warnings.filterwarnings("ignore", category=UserWarning)
import ui, communication
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"
import pygame


#----------------------When using keyboard---------------------------------

def Mute(event, is_muted):
    if event.type == pygame.KEYDOWN and event.key == pygame.K_m:
        is_muted = not is_muted
        ui.is_muted = is_muted
        if is_muted:
            pygame.mixer.music.pause()
        else:
            pygame.mixer.music.unpause()
    return is_muted

def next_level(event,is_next_level):
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_RETURN:
            is_next_level = not is_next_level

    return is_next_level

# Stop music function
def stop_music():
    pygame.mixer.music.stop()


#-------------------------------- When using Aetherlink -----------------------------------

# Background music controlled using left pot
def get_volume_trans():
    return max(0.0, min(1.0, int(communication.left_pot) / 1023))

# Player movement using joystick - Right/Left
def get_joystick_2_x():
    return communication.right_joystick_x

# Player movement using joystick - Jump and shooting
def get_joystick_1_y():
    return communication.left_joystick_y

# Enter/Restart
def get_toggle():
    return communication.right_toggle_switch

# Open the main menu / Pause
def get_btn1():
    return communication.left_button

# Redirect to homepage
def get_btn2():
    return communication.right_button