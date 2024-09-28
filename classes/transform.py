from __future__ import annotations
from classes.vec3 import Vec3
import pyrr.matrix44 as mat4
import numpy as np
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from classes.gameobject import GameObject

class Transform:
    def __init__(self, pos: Vec3, scale: Vec3, rotation: Vec3) -> None:
        self.pos = pos
        self.scale = scale
        self.rotation = rotation
        self.model_matrix = mat4.create_identity()
    
    @staticmethod
    def zero():
        return Transform(Vec3.zero(), Vec3.zero(), Vec3.zero())
        
        
@staticmethod
def create_model_matrix(transform: Transform) -> np.ndarray:
    model_matrix = mat4.create_identity(dtype=np.float32)
    model_matrix = mat4.multiply(model_matrix, mat4.create_from_scale(transform.scale.to_list(), dtype=np.float32))
    model_matrix = mat4.multiply(model_matrix, mat4.create_from_axis_rotation([1, 0, 0], transform.rotation.x, dtype=np.float32))
    model_matrix = mat4.multiply(model_matrix, mat4.create_from_axis_rotation([0, 0, 1], transform.rotation.y, dtype=np.float32))
    model_matrix = mat4.multiply(model_matrix, mat4.create_from_axis_rotation([0, 1, 0], transform.rotation.z, dtype=np.float32))
    # model_matrix = mat4.multiply(model_matrix, mat4.create_from_eulers(transform.rotation.to_list(), dtype=np.float32))
    model_matrix = mat4.multiply(model_matrix, mat4.create_from_translation(transform.pos.to_list(), dtype=np.float32))
    return model_matrix

def create_entire_model_matrix(transform: Transform, parent: None | GameObject = None, passed_model_matrix = None) -> np.ndarray:
    model_matrix = mat4.create_identity()
    if type(passed_model_matrix) != type(None):
        model_matrix = passed_model_matrix
    model_matrix = mat4.multiply(model_matrix, create_model_matrix(transform))
    if parent:
        return create_entire_model_matrix(parent.local_transform, parent.parent, model_matrix)
    return model_matrix