import sys, pygame
from pygame.locals import *
import time
import subprocess
import os
from subprocess import *
os.environ["SDL_FBDEV"] = "/dev/fb1"
os.environ["SDL_MOUSEDEV"] = "/dev/input/touchscreen"
os.environ["SDL_MOUSEDRV"] = "TSLIB"

# Initialize pygame and hide mouse
pygame.init()
pygame.mouse.set_visible(0)


size = width, height = 480, 320
screen = pygame.display.set_mode(size)



screen.fill(red)
pygame.display.update()





class Icon:

        def __init__(self, name):
                self.name = name
                try:
                        self.bitmap = pygame.image.load(f'{iconPath}/{name}.png')
                except:
                  pass
