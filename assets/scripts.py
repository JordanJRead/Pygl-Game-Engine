from classes.monobehaviour import MonoBehaviour
import pygame as pg
from math import pi, cos, sin
from classes.transform import Transform
from classes.vec3 import Vec3
import pyrr.matrix44 as mat4
import numpy as np
from OpenGL.GL import *
from classes.texture import Texture2D
from classes import gameobject

class PlayerMove(MonoBehaviour):
    def __init__(self, speed: float, sens: float, width: int, height: int) -> None:
        super().__init__()
        self.speed = speed
        self.sens = sens
        self.pitch = 0
        self.yaw = 0
        self.width = width
        self.height = height
        # self.prev_mouse_position = (width/2, height/2)
        self.prev_mouse_position = pg.mouse.get_pos()

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
        self.game_object.update_transform(Transform(self.game_object.transform.pos, self.game_object.transform.scale, Vec3(self.pitch, 0, self.yaw)))

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

        self.game_object.update_transform(Transform(self.game_object.transform.pos + move_vector, self.game_object.transform.scale, self.game_object.transform.rotation))
    
    def get_view_matrix(self, usePosition = True):
        camera_matrix = mat4.create_identity(dtype=np.float32)
        camera_matrix = mat4.multiply(camera_matrix, mat4.create_from_axis_rotation([1, 0, 0], self.pitch, dtype=np.float32))
        camera_matrix = mat4.multiply(camera_matrix, mat4.create_from_axis_rotation([0, 1, 0], self.yaw, dtype=np.float32))
        if usePosition:
            camera_matrix = mat4.multiply(camera_matrix, mat4.create_from_translation(self.game_object.transform.pos.to_list()))
        return mat4.inverse(camera_matrix)

class RenderScript(MonoBehaviour):
    def __init__(self, obj_path: str, image_path: str) -> None:
        self.active = False
        if obj_path:
            self.active = True
        if self.active:
            self.model_matrix = mat4.create_identity()
            self.vertices = self.load_obj(obj_path)

            self.vbo = glGenBuffers(1)
            glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
            glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)

            self.vao = glGenVertexArrays(1)
            glBindVertexArray(self.vao)
            
            glEnableVertexAttribArray(0)
            glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 8 * 4, ctypes.c_void_p(0))
            
            glEnableVertexAttribArray(1)
            glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 8 * 4, ctypes.c_void_p(3 * 4))

            glEnableVertexAttribArray(2)
            glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 8 * 4, ctypes.c_void_p(6 * 4))

            self.texture2d = Texture2D(image_path)
    
    def start(self):
        self.model_matrix = self.create_entire_model_matrix(self.game_object.transform, self.game_object.parent)
        

    def create_model_matrix(self, transform: Transform) -> np.ndarray:
        model_matrix = mat4.create_identity(dtype=np.float32)
        model_matrix = mat4.multiply(model_matrix, mat4.create_from_scale(transform.scale.to_list(), dtype=np.float32))
        model_matrix = mat4.multiply(model_matrix, mat4.create_from_eulers(transform.rotation.to_list(), dtype=np.float32))
        model_matrix = mat4.multiply(model_matrix, mat4.create_from_translation(transform.pos.to_list(), dtype=np.float32))
        return model_matrix

    def create_entire_model_matrix(self, transform: Transform, parent = None, passed_model_matrix = None, inverse = False) -> np.ndarray:
        model_matrix = mat4.create_identity()
        if type(passed_model_matrix) != type(None):
            model_matrix = passed_model_matrix
        model_matrix = mat4.multiply(model_matrix, self.create_model_matrix(transform))
        if parent:
            return self.create_entire_model_matrix(parent.transform, parent.parent, model_matrix, inverse)
        if inverse:
            return mat4.inverse(model_matrix)
        return model_matrix
    
    def load_obj(self, file_path: str) -> np.ndarray:
        vertices: list[float] = [] # x y z nx ny nz u v x y z nx ny nz u v...

        faces: list[str] = [] # ["1/6/3", "p/t/n"] 
        positions = [] # [["x", "y", "z"], ["x", "y", "z"]...]
        normals = [] # [["x", "y", "z"], ["x", "y", "z"]...]
        uvs = [] # [["u", "v"], ["u", "v"], ["u", "v"]...]
        with open(file_path) as file:
            file = [l.strip('\n\r') for l in file]
            for line in file:
                split_line = line.split(" ")
                split_line = [x for x in split_line if x != ""]
                match split_line[0]:
                    case "v":
                        positions.append([split_line[1], split_line[2], split_line[3]])
                    case "vt":
                        uvs.append([split_line[1], split_line[2]])
                    case "vn":
                        normals.append([split_line[1], split_line[2], split_line[3]])
                    case "f":
                        # A triangle. Each index (1, 2, 3) is a vertice
                        faces.append(split_line[1]) # "0/0/0"
                        faces.append(split_line[2])
                        faces.append(split_line[3])
                        
            for face in faces:
                indices = face.split("/") # ["1", "6", "3"]
                indices = [int(num) for num in indices]
                position = positions[indices[0]]
                uv = uvs[indices[1]]
                normal = normals[indices[2]]
                vertices.extend([int(num) for num in position])
                vertices.extend([int(num) for num in normal])
                vertices.extend([int(num) for num in uv])
        
        return np.array(vertices, dtype=np.float32)