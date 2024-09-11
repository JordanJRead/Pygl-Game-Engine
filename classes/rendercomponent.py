from classes.texture import Texture2D
import pyrr.matrix44 as mat4
from classes.transform import Transform
import numpy as np
from OpenGL.GL import *

class RenderComponent:
    def __init__(self, obj_path: str, image_path: str) -> None:
        self.active = False
        self.is_bright = False
        if obj_path:
            self.active = True
        if self.active:
            self.model_matrix = mat4.create_identity()
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
        if self.active:
            self.texture2d.destroy()
            glDeleteBuffers(1, (self.vbo,))
            glDeleteVertexArrays(1, (self.vao,))

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

def create_model_matrix(transform: Transform) -> np.ndarray:
    model_matrix = mat4.create_identity(dtype=np.float32)
    model_matrix = mat4.multiply(model_matrix, mat4.create_from_scale(transform.scale.to_list(), dtype=np.float32))
    model_matrix = mat4.multiply(model_matrix, mat4.create_from_eulers(transform.rotation.to_list(), dtype=np.float32))
    model_matrix = mat4.multiply(model_matrix, mat4.create_from_translation(transform.pos.to_list(), dtype=np.float32))
    return model_matrix

def create_entire_model_matrix(transform: Transform, parent = None, passed_model_matrix = None, inverse = False) -> np.ndarray:
    model_matrix = mat4.create_identity()
    if type(passed_model_matrix) != type(None):
        model_matrix = passed_model_matrix
    model_matrix = mat4.multiply(model_matrix, create_model_matrix(transform))
    if parent:
        return create_entire_model_matrix(parent.transform, parent.parent, model_matrix, inverse)
    if inverse:
        return mat4.inverse(model_matrix)
    return model_matrix
