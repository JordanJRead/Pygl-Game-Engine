import pygame as pg

class UISettings:
    def __init__(self, hierarchy_rect: pg.Rect, hierarchy_color: tuple[int, int, int]) -> None:
        self.hierarchy_rect = hierarchy_rect
        self.hierarchy_color = hierarchy_color

class Colors:
    def __init__(self) -> None:
        self.dark_green = (22, 32, 20)
        self.light_green = (76,100,68)