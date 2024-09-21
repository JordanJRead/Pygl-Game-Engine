from __future__ import annotations
import pygame as pg
import pygame_gui as pgui
from classes.gameobject import GameObject
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from main import App

class Hierarchy:
    def __init__(self, rect: pg.Rect, ui_manager: pgui.UIManager, game_objects: list[GameObject]) -> None:
        self.panel = pgui.elements.UIPanel(rect, manager=ui_manager)
        self.rect = rect
        self.ui_manager = ui_manager
        self.game_objects = game_objects
        self.game_object_buttons: dict[pgui.core.UIElement, GameObject] = {}
        self.build_buttons(None)
    
    def build_buttons(self, selected_object: GameObject | None = None):
        self.kill_buttons()
        self.y_depth = 0
        for game_object in self.game_objects:
            self.create_buttons(game_object, selected_object)

    def create_buttons(self, game_object: GameObject, selected_object: GameObject, x_depth: int = 0):
        top_margin = 10
        left_margin = 10
        size = 50
        depth_offset = 50

        x = left_margin + depth_offset * x_depth
        y = top_margin + size * self.y_depth

        if selected_object == game_object:
            self.game_object_buttons[pgui.elements.UIButton(pg.Rect((x, y), (100, 50)), game_object.name, self.ui_manager, container=self.panel, object_id="@bright_button")] = game_object
        else:
            self.game_object_buttons[pgui.elements.UIButton(pg.Rect((x, y), (100, 50)), game_object.name, self.ui_manager, container=self.panel)] = game_object

        self.y_depth += 1
        for child in game_object.children:
            self.create_buttons(child, selected_object, x_depth + 1)
    
    def kill_buttons(self):
        for button in self.game_object_buttons:
            button.kill()

class Inspector:
    def __init__(self, rect: pg.Rect, ui_manager: pgui.UIManager, game_object: GameObject | None = None) -> None:
        self.ui_id = "#inspector_name"
        self.game_object = game_object
        self.ui_manager = ui_manager
        self.rect = rect
        self.panel = pgui.elements.UIPanel(rect, manager=ui_manager)
        self.name_input: pgui.elements.UITextEntryLine | None = None
        self.delete_button: pgui.elements.UIButton | None = None
        delete_button_size = 50
        delete_button_padding = 10
        self.delete_button_rect = pg.Rect(self.panel.relative_rect.width - delete_button_padding - delete_button_size, delete_button_padding, delete_button_size, delete_button_size)
    
    def set_game_object(self, game_object: GameObject | None):
        self.destroy()
        self.game_object = game_object
        self.create()

    def destroy(self):
            if not self.game_object is None:
                self.name_input.kill()
                self.name_input = None
                self.delete_button.kill()

    def create(self):
        if self.game_object:
            self.name_input = pgui.elements.UITextEntryLine(pg.Rect(0, 40, 100, 50), self.ui_manager, anchors={"centerx": "centerx"}, placeholder_text=self.game_object.name, object_id=self.ui_id, container=self.panel)
            self.delete_button = pgui.elements.UIButton(self.delete_button_rect, "", self.ui_manager, object_id="@delete_button", container=self.panel)

class CreationButtons:
    def __init__(self, bottom_rect: pg.Rect, ui_manager: pgui.UIManager) -> None:
        self.bottom_rect = bottom_rect
        self.ui_manager = ui_manager
        self.button_width = 190
        self.button_height = 50
        self.button_width_gap = 5
        self.button_height_gap = 5
        self.create_top_level_button = pgui.elements.UIButton(pg.Rect(self.bottom_rect.centerx - self.button_width_gap/2 - self.button_width, self.bottom_rect.top - self.button_height - self.button_height_gap, self.button_width, self.button_height), "Create Game Object")
        self.child_button_rect = pg.Rect(self.bottom_rect.centerx + self.button_width_gap/2, self.bottom_rect.top - self.button_height - self.button_height_gap, self.button_width, self.button_height)
        self.child_button = pgui.elements.UIButton(self.child_button_rect, "Create Child Game Object", object_id="@grey_button")
    
    def enable_child_button(self):
        self.child_button.kill()
        self.child_button = pgui.elements.UIButton(self.child_button_rect, "Create Child Game Object")

    def disable_child_button(self):
        self.child_button.kill()
        self.child_button = pgui.elements.UIButton(self.child_button_rect, "Create Child Game Object", object_id="@grey_button")