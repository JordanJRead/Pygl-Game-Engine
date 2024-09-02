import pygame as pg
from OpenGL.GL import *

class Texture2D:
    def __init__(self, image_path: str) -> None:
        image = pg.image.load(image_path).convert_alpha()
        image_data = pg.image.tostring(image, "RGBA")

        self.ref = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.ref)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image.get_width(), image.get_height(), 0, GL_RGBA, GL_UNSIGNED_BYTE, image_data)

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    
    def use(self):
        glBindTexture(GL_TEXTURE_2D, self.ref)

    def destroy(self):
        glDeleteTextures(1, (self.ref,))