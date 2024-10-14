from math import sqrt
import pyrr.matrix44 as mat4
import numpy as np

class Vec3:

    def __init__(self, x: float, y: float, z: float) -> None:
        self.x = x
        self.y = y
        self.z = z
    
    def __add__(self, other):
        if type(other) == Vec3:
            return Vec3(self.x + other.x, self.y + other.y, self.z + other.z)
        raise TypeError
    
    def __sub__(self, other):
        if type(other) == Vec3:
            return Vec3(self.x - other.x, self.y - other.y, self.z - other.z)
        raise TypeError
    
    def __mul__(self, other):
        if type(other) in [float, int]:
            return Vec3(self.x * other, self.y * other, self.z * other)
        elif type(other) == Vec3: # Dot product
            return self.x * other.x + self.y * other.y + self.z * other.z
        raise TypeError
    
    def __truediv__(self, other):
        if type(other) in [float, int]:
            return Vec3(self.x / other, self.y / other, self.z / other)
    
    def __abs__(self):
        return sqrt(self.x**2 + self.y**2 + self.z**2)
    
    def __len__(self):
        return 3
    
    def to_list(self):
        return [self.x, self.y, self.z]
    
    def normalize(self):
        if abs(self) != 0:
            return self / abs(self)
        return self
    
    def cross(self, other):
        if type(other) != Vec3:
            raise TypeError
        return Vec3(self.y * other.z - self.z * other.y, self.z * other.x - self.x * other.z, self.x * other.y - self.y * other.x)
    
    def vec_mul(self, other):
        """Multiplies each component of self by the corrosponding component in other"""
        if type(other) != Vec3:
            raise TypeError
        return Vec3(self.x * other.x, self.y * other.y, self.z * other.z)
    
    def vec_div(self, other):
        """Divides each component of self by the corrosponding component in other"""
        if type(other) != Vec3:
            raise TypeError
        return Vec3(self.x / other.x, self.y / other.y, self.z / other.z)
    
    def mat_mul(self, other) -> tuple[float, float, float, float]:
        """Vec3 times a 4x4 row-majored matrix"""
        if type(other) == np.ndarray and type(other[0]) == np.ndarray:
            # Vec4 = namedtuple('Vec4', "x y z w")
            # self4 = Vec4(self.x, self.y, self.z, 1)
            # return Vec3(
            #     self4.x * other[0][0] + self4.y * other[0][1] + self4.z * other[0][2] + self4.w * other[0][3],
            #     self4.x * other[1][0] + self4.y * other[1][1] + self4.z * other[1][2] + self4.w * other[1][3],
            #     self4.x * other[2][0] + self4.y * other[2][1] + self4.z * other[2][2] + self4.w * other[2][3]
            # )
            return mat4.multiply(other, [self.x, self.y, self.z, 1])
        raise TypeError
    
    @staticmethod
    def zero():
        return Vec3(0, 0, 0)

    @staticmethod
    def one():
        return Vec3(1, 1, 1)
    
    @staticmethod
    def up():
        return Vec3(0, 1, 0)
    
    @staticmethod
    def down():
        return Vec3(0, -1, 0)
    
    @staticmethod
    def left():
        return Vec3(-1, 0, 0)
    
    @staticmethod
    def right():
        return Vec3(1, 0, 0)
    
    @staticmethod
    def forward():
        return Vec3(0, 0, 1)
    
    @staticmethod
    def backward():
        return Vec3(0, 0, -1)