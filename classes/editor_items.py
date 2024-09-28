from __future__ import annotations
import pygame as pg
import pygame_gui as pgui
from classes.gameobject import GameObject
from classes.transform import Transform
from classes.vec3 import Vec3

class InputPanel:
    def __init__(self, rect: pg.Rect, button_size: tuple[float, float], row_count: int, row_size: int, default_values: list, function: function, container: pgui.core.IContainerLikeInterface, ui_manager: pgui.UIManager, x_padding = 10, y_padding = 70, row_labels: list[str] = [""], item_labels: list[list[str]] = [[""]]) -> None:
        self.rect = rect
        self.button_size = button_size
        self.row_count = row_count
        self.row_size = row_size
        self.function = function
        self.default_values = default_values
        self.ui_manager = ui_manager
        self.panel = pgui.elements.UIPanel(self.rect, manager=self.ui_manager, container=container, object_id="@dark_panel")
        self.rows: list[list[pgui.elements.UITextEntryLine]] = []

        for row_num in range(self.row_count):
            row = []
            # pgui.elements.UILabel(pg.Rect()) # TODO                                       
            for col_num in range(self.row_size):
                index = col_num + self.row_count * row_num
                row.append(pgui.elements.UITextEntryLine(
                    relative_rect=pg.Rect(
                        x_padding * (col_num + 1) + col_num * self.button_size[0],
                        y_padding * (row_num + 1) + row_num * self.button_size[1],
                        self.button_size[0],
                        self.button_size[1]
                        ),
                    manager=self.ui_manager,
                    container=self.panel,
                    initial_text=str(default_values[index]),
                    placeholder_text=str(default_values[index])
                    ))
            self.rows.append(row)

    def destroy(self):
        self.panel.kill()
        for row in self.rows:
            for field in row:
                field.kill()

class Hierarchy:
    def __init__(self, rect: pg.Rect, ui_manager: pgui.UIManager, game_objects: list[GameObject]) -> None:
        self.panel = pgui.elements.UIScrollingContainer(rect, ui_manager, object_id="@scroll_panel")
        # self.panel = pgui.elements.UIPanel(rect, manager=ui_manager, object_id="@scroll_panel")
        self.rect = rect
        self.ui_manager = ui_manager
        self.game_objects = game_objects
        self.game_object_buttons: dict[pgui.core.UIElement, GameObject] = {}
        self.moving = False
        self.move_button: pgui.elements.UIButton | None = None
        self.largest_x = 0
        self.largest_y = 0
        self.build_buttons(None)

    
    def build_buttons(self, selected_object: GameObject | None = None):
        self.kill_buttons()
        self.y_depth = 0
        self.largest_x = 0
        self.largest_y = 0
        for game_object in self.game_objects:
            self.create_buttons(game_object, selected_object)

    def create_buttons(self, game_object: GameObject, selected_object: GameObject, x_depth: int = 0):
        top_margin = 10
        left_margin = 10
        size = 50
        depth_offset = 50

        x = left_margin + depth_offset * x_depth
        y = top_margin + size * self.y_depth

        if x > self.largest_x:
            self.largest_x = x
        if x > self.largest_y:
            self.largest_y = y

        if selected_object == game_object:
            selected_button = pgui.elements.UIButton(pg.Rect((x, y), (100, 50)), game_object.name, self.ui_manager, container=self.panel, object_id="@bright_button")
            self.game_object_buttons[selected_button] = game_object
            self.move_button = pgui.elements.UIButton(pg.Rect(x + 100 + 10, y, 50, 50), "", self.ui_manager, self.panel, object_id="@move_button")
        else:
            self.game_object_buttons[pgui.elements.UIButton(pg.Rect((x, y), (100, 50)), game_object.name, self.ui_manager, container=self.panel)] = game_object

        self.y_depth += 1
        for child in game_object.children:
            self.create_buttons(child, selected_object, x_depth + 1)
            
        self.panel.set_scrollable_area_dimensions((x + 70, self.largest_y + 10))
    
    def kill_buttons(self):
        for button in self.game_object_buttons:
            button.kill()
        if self.move_button:
            self.move_button.kill()

    def toggle_move_button(self):
        if not self.moving:
            self.move_button.change_object_id("@move_button_dark")
        else:
            self.move_button.change_object_id("@move_button")
        self.moving = not self.moving

class Inspector:
    def __init__(self, rect: pg.Rect, ui_manager: pgui.UIManager, game_object: GameObject | None = None) -> None:
        self.game_object = game_object
        self.ui_manager = ui_manager
        self.rect = rect
        self.panel = pgui.elements.UIPanel(rect, manager=ui_manager)
        self.name_input: pgui.elements.UITextEntryLine | None = None

        self.delete_button: pgui.elements.UIButton | None = None
        delete_button_size = 50
        delete_button_padding = 10
        self.delete_button_rect = pg.Rect(self.panel.relative_rect.width - delete_button_padding - delete_button_size, delete_button_padding, delete_button_size, delete_button_size)

        self.transform_panel_rect = pg.Rect(
            self.panel.rect.width * 0.05,
            self.panel.rect.height * 0.08,
            self.panel.rect.width * 0.9,
            self.panel.rect.height * 0.2
            )
        
        self.input_panels: list[InputPanel] = []

    @staticmethod
    def transform_update_function(game_object: GameObject, rows: list[list[pgui.elements.UITextEntryLine]]):
        new_transform = Transform(
            Vec3(float(rows[0][0].text), float(rows[0][1].text), float(rows[0][2].text)),
            Vec3(float(rows[1][0].text), float(rows[1][1].text), float(rows[1][2].text)),
            Vec3(float(rows[2][0].text), float(rows[2][1].text), float(rows[2][2].text))
        )
        game_object.update_transform(new_transform)

    def set_game_object(self, game_object: GameObject | None):
        self.destroy()
        self.game_object = game_object
        self.create()

    def destroy(self):
            if not self.game_object is None:
                self.name_input.kill()
                self.name_input = None
                self.delete_button.kill()
                for input_panel in self.input_panels:
                    input_panel.destroy()
                self.input_panels.clear()

    def create(self):
        if self.game_object:
            self.name_input = pgui.elements.UITextEntryLine(pg.Rect(0, 40, 100, 50), self.ui_manager, anchors={"centerx": "centerx"}, placeholder_text=self.game_object.name, container=self.panel)

            default_values = []
            default_values.extend(self.game_object.local_transform.pos.to_list())
            default_values.extend(self.game_object.local_transform.scale.to_list())
            default_values.extend(self.game_object.local_transform.rotation.to_list())


            transform_panel = InputPanel(
            rect=self.transform_panel_rect,
            button_size=(self.rect.width / 4, 50),
            row_count=3,
            row_size=3,
            default_values=default_values,
            function=self.transform_update_function,
            container=self.panel,
            ui_manager=self.ui_manager,
            x_padding=self.panel.rect.width / 16,
            y_padding=20
            )

            self.input_panels.append(transform_panel)

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