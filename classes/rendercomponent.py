from __future__ import annotations
from classes.texture import Texture2D
import numpy as np
from OpenGL.GL import *

class RenderComponent:
    def __init__(self, obj_path: str, image_path: str, active=True) -> None:
        self.image_path = image_path
        self.obj_path = obj_path
        self.is_active = active
        if obj_path == "" or image_path == "":
            self.is_active = False
        self.is_bright = False
        if self.is_active:
            self.vertices = load_obj(obj_path)

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

    def destroy(self):
        if self.is_active:
            self.texture2d.destroy()
            glDeleteBuffers(1, (self.vbo,))
            glDeleteVertexArrays(1, (self.vao,))
    
    def update_paths(self, obj_path: str, image_path: str):
        self.destroy()
        self.__init__(obj_path, image_path)

def load_obj(file_path: str) -> np.ndarray:
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