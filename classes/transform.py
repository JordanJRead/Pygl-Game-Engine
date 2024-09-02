from classes.vec3 import Vec3

class Transform:
    def __init__(self, pos: Vec3, scale: Vec3, rotation: Vec3) -> None:
        self.pos = pos
        self.scale = scale
        self.rotation = rotation