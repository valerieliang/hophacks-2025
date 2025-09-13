import pygame
import os

pygame.font.init()

# Path to your font file
BASE_DIR = os.path.dirname(__file__)
DYNAPUFF_PATH = os.path.join(BASE_DIR, "DynaPuff-VariableFont_wdth,wght.ttf")

def dynapuff(size, bold=False, italic=False):
    """
    Returns a pygame Font object for DynaPuff
    size: font size
    bold: make font bold (if supported)
    italic: make font italic (if supported)
    """
    font = pygame.font.Font(DYNAPUFF_PATH, size)
    font.set_bold(bold)
    font.set_italic(italic)
    return font
