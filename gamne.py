import pygame
import time
pygame.mixer.init(44100, -16,2,4096)
pygame.mixer.music.load('0863.ogg')
pygame.mixer.music.play()
time.sleep(5)
