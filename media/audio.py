import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

import pygame
import time 
def on_win(play):
    if play:
        pygame.mixer.init()
        pygame.mixer.music.load("./media/secret.mp3")
        pygame.mixer.music.play()
        time.sleep(5)  # Wait for 5 seconds
        pygame.mixer.music.stop()  # Stop playback