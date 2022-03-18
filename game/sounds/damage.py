import pygame 
from pygame.mixer import Sound
pygame.init()
laser = Sound("E:/game/sounds/laser.wav")
while True:
    laser.play()