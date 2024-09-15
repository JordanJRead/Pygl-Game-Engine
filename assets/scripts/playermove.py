from classes.monobehaviour import MonoBehaviour
from classes.transform import Transform
from classes.vec3 import Vec3
import pygame as pg
from math import pi, cos, sin
from OpenGL.GL import *

"""This class changes the object's transform based on user input"""
class PlayerMove(MonoBehaviour):
    def __init__(self, game_object, app, speed: float, sens: float) -> None:
        super().__init__(game_object, app)
        self.speed = speed
        self.sens = sens
        self.pitch = 0
        self.yaw = 0
        self.prev_mouse_position = pg.mouse.get_pos()
        self.width = self.app.width
        self.height = self.app.height

    def update(self):
        self.rotate()
        self.move()

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
        if not (self.width/4 < current_mouse_x < 3 * (self.width/4)):
            pg.mouse.set_pos(self.width/2, self.height/2)
        if not (self.height/4 < current_mouse_y < 3 * (self.height/4)):
            pg.mouse.set_pos(self.width/2, self.height/2)
        self.prev_mouse_position = pg.mouse.get_pos()
        self.game_object.update_transform(Transform(self.game_object.local_transform.pos, self.game_object.local_transform.scale, Vec3(self.pitch, 0, self.yaw)))

    def move(self):
        move_vector = Vec3(0, 0, 0)
        keys = pg.key.get_pressed()
        if keys[pg.K_a]:
            move_vector.x -= 1
        if keys[pg.K_d]:
            move_vector.x += 1
        if keys[pg.K_LSHIFT]:
            move_vector.y -= 1
        if keys[pg.K_SPACE]:
            move_vector.y += 1
        if keys[pg.K_s]:
            move_vector.z -= 1
        if keys[pg.K_w]:
            move_vector.z += 1
        move_vector = move_vector.normalize() * self.speed * self.delta_time
        
        move_vector = Vec3(move_vector.x * cos(-self.yaw) - move_vector.z * sin(-self.yaw), move_vector.y, move_vector.x * sin(-self.yaw) + move_vector.z * cos(-self.yaw))

        self.game_object.update_transform(Transform(self.game_object.local_transform.pos + move_vector, self.game_object.local_transform.scale, self.game_object.local_transform.rotation))