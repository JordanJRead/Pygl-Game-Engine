from __future__ import annotations
from classes.gameobject import GameObject
from math import tan, radians
import numpy as np
from OpenGL.GL import *
from classes.monobehaviour import MonoBehaviour
import pyrr.matrix44 as mat4
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from main import App


class Camera(MonoBehaviour):
    def __init__(self, game_object: GameObject, app: App, near_distance: float, far_distance: float, horizontal_fov_deg: float) -> None:
        super().__init__(game_object, app)
        self.near_distance = near_distance
        self.far_distance = far_distance
        self.aspect_ratio = self.app.width / self.app.height
        self.horizontal_fov_deg = horizontal_fov_deg
        self.projection_matrix = self.get_projection_matrix()
    
        # Framebuffer
        self.fbo = glGenFramebuffers(1)
        glBindFramebuffer(GL_FRAMEBUFFER, self.fbo)

        # Texture
        self.color_texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.color_texture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self.app.width, self.app.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, None)

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)

        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, self.color_texture, 0)

        # Depth buffer
        self.depth_texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.depth_texture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_DEPTH_COMPONENT32F, self.app.width, self.app.height, 0, GL_DEPTH_COMPONENT, GL_FLOAT, None)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_TEXTURE_2D, self.depth_texture, 0)

    def update(self):
        self.app.renderer.render_objects_to_fbo(self.app.game_objects, self.projection_matrix, mat4.inverse(self.game_object.local_transform.model_matrix), self.fbo, flip=False)

    def end(self):
        glDeleteFramebuffers(1, (self.fbo,))
        glDeleteTextures(2, (self.color_texture, self.depth_texture))
    
    def get_projection_matrix(self):
        width = self.near_distance*tan(radians(self.horizontal_fov_deg / 2))
        height = width / self.aspect_ratio

        a = (self.near_distance + self.far_distance) / (self.far_distance - self.near_distance)
        b = (-2 * self.far_distance * self.near_distance) / (self.far_distance - self.near_distance)

        projection = np.array([
            [self.near_distance / width, 0,                           0, 0],
            [0,                          self.near_distance / height, 0, 0],
            [0,                          0,                           a, b],
            [0,                          0,                           1, 0]
        ], dtype=np.float32)

        return projection