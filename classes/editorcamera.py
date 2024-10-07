import pygame as pg
from math import pi, sin, cos, tan, radians
from classes.vec3 import Vec3
import pyrr.matrix44 as mat4
import numpy as np

class EditorCamera:
    def __init__(self, speed: float, sens: float, width: int, height: int, viewport: tuple[int, int, int, int], near_distance: float, far_distance: float, horizontal_fov_deg: float, aspect_ratio: float) -> None:
        self.speed = speed
        self.sens = sens
        self.width = width
        self.height = height
        self.pitch = 0
        self.yaw = 0
        self.pos = Vec3(0, 0, 0)
        self.prev_mouse_position = pg.mouse.get_pos()
        self.rotation = Vec3(0, 0, 0)
        self.viewport = viewport
        self.near_distance = near_distance
        self.far_distance = far_distance
        self.horizontal_fov_deg = horizontal_fov_deg
        self.aspect_ratio = aspect_ratio
        self.projection_matrix = self.get_projection_matrix()

    def update(self, delta_time):
        self.rotate()
        self.move(delta_time)

    def rotate(self):
        current_mouse_x = pg.mouse.get_pos()[0]
        delta_mouse_x = current_mouse_x - self.prev_mouse_position[0]
        self.yaw += delta_mouse_x * self.sens
        if self.yaw > 2 * pi:
            self.yaw -= 2 * pi
        if self.yaw < 0:
            self.yaw += 2 * pi
        
        current_mouse_y = pg.mouse.get_pos()[1]
        delta_mouse_y = current_mouse_y - self.prev_mouse_position[1]
        self.pitch += delta_mouse_y * self.sens
        if self.pitch >= pi / 2:
            self.pitch = pi / 2 -0.001
        if self.pitch <= -pi / 2:
            self.pitch = -pi / 2 + 0.001
        
        # Keep mouse from moving off screen
        middle_pos = (self.viewport[0] + self.viewport[2] // 2, self.height - self.viewport[1] - self.viewport[3] // 2)
        if not (self.viewport[0] < current_mouse_x < self.viewport[0] + self.viewport[2]):
            pg.mouse.set_pos(*middle_pos)
        if not (self.height - self.viewport[1] - self.viewport[3] < current_mouse_y < self.height - self.viewport[1]):
            pg.mouse.set_pos(*middle_pos)

        self.prev_mouse_position = pg.mouse.get_pos()
        self.rotataion = Vec3(self.pitch, 0, self.yaw)

    def move(self, delta_time):
        move_vector = Vec3(0, 0, 0)
        keys = pg.key.get_pressed()
        if keys[pg.K_a]:
            move_vector.x -= 1
        if keys[pg.K_d]:
            move_vector.x += 1
        if keys[pg.K_LCTRL]:
            move_vector.y -= 1
        if keys[pg.K_SPACE]:
            move_vector.y += 1
        if keys[pg.K_s]:
            move_vector.z -= 1
        if keys[pg.K_w]:
            move_vector.z += 1
        move_vector = move_vector.normalize() * self.speed * delta_time
        if keys[pg.K_LSHIFT]:
            move_vector *= 2
        
        move_vector = Vec3(move_vector.x * cos(-self.yaw) - move_vector.z * sin(-self.yaw), move_vector.y, move_vector.x * sin(-self.yaw) + move_vector.z * cos(-self.yaw))
        self.pos += move_vector
    
    def get_view_matrix(self, usePosition = True):
        camera_matrix = mat4.create_identity(dtype=np.float32)
        camera_matrix = mat4.multiply(camera_matrix, mat4.create_from_axis_rotation([1, 0, 0], self.pitch, dtype=np.float32))
        camera_matrix = mat4.multiply(camera_matrix, mat4.create_from_axis_rotation([0, 1, 0], self.yaw, dtype=np.float32))
        if usePosition:
            camera_matrix = mat4.multiply(camera_matrix, mat4.create_from_translation(self.pos.to_list()))
        return mat4.inverse(camera_matrix)
    
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