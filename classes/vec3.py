from math import sqrt

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