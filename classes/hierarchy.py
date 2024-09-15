import pygame as pg
import pygame_gui as pgui
from classes.gameobject import GameObject

class Hierarchy:
    def __init__(self, rect: pg.Rect, ui_manager: pgui.UIManager, game_objects: list[GameObject]) -> None:
        self.panel = pgui.elements.UIPanel(rect, manager=ui_manager)
        self.ui_manager = ui_manager
        self.game_objects = game_objects
        self.game_object_buttons: dict[pgui.core.UIElement, GameObject] = {}
        self.build_buttons()
    
    def build_buttons(self):
        self.kill_buttons()
        self.y_depth = 0
        for game_object in self.game_objects:
            self.create_buttons(game_object, self.y_depth)

    def create_buttons(self, game_object: GameObject, y_depth, x_depth: int = 0):
        top_margin = 10
        left_margin = 10
        size = 50
        depth_offset = 50

        x = left_margin + depth_offset * x_depth
        y = top_margin + size * y_depth
        self.game_object_buttons[pgui.elements.UIButton(pg.Rect((x, y), (100, 50)), game_object.name, self.ui_manager, container=self.panel)] = game_object
        self.y_depth += 1
        for child in game_object.children:
            self.create_buttons(child, self.y_depth, x_depth + 1)
    
    def kill_buttons(self):
        for button in self.game_object_buttons:
            button.kill()