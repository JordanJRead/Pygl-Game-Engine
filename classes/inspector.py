from classes.gameobject import GameObject
import pygame_gui as pgui
import pygame as pg

class Inspector:
    def __init__(self, rect: pg.Rect, ui_manager: pgui.UIManager, game_object: GameObject | None = None) -> None:
        self.ui_id = "#inspector_name"
        self.game_object = game_object
        self.ui_manager = ui_manager
        self.panel = pgui.elements.UIPanel(rect, manager=ui_manager)
        self.name_input: pgui.elements.UITextEntryLine | None = None
    
    def set_game_object(self, game_object: GameObject | None):
        self.game_object = game_object
        if self.name_input:
            self.name_input.kill()
        if game_object:
            self.name_input = pgui.elements.UITextEntryLine(pg.Rect(0, 40, 100, 50), self.ui_manager, anchors={"centerx": "centerx"}, placeholder_text=self.game_object.name, object_id=self.ui_id, container=self.panel)
        else:
            self.name_input = None