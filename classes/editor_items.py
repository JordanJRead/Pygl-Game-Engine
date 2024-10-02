from __future__ import annotations
import pygame as pg
import pygame_gui as pgui
from classes.gameobject import GameObject
from classes.transform import Transform
from classes.vec3 import Vec3

class InputPanel:
    def __init__(self,
                 parent_width: float,
                 left_margin: float,
                 top: float,
                 default_values: list[list],
                 function: function,
                 container: pgui.core.IContainerLikeInterface, 
                 ui_manager: pgui.UIManager,
                 title: str,
                 row_labels: list[str] = [""], 
                 item_labels: list[list[str]] = [[""]]) -> None:
        
        self.row_count = len(default_values)
        self.row_size = len(default_values[0])
        self.function = function
        self.default_values = default_values

        # Hard coded styling constatnts
        self.x_padding = 10
        self.text_y_margin = 5
        self.text_height = 30
        self.row_height = 30
        self.row_y_margin = 5
        self.bottom_padding = 10

        self.width = parent_width - left_margin * 2
        self.padded_width = self.width - self.x_padding * 2
        self.height = (
            self.text_y_margin
            + self.text_height
            + self.text_y_margin

            + self.row_count *
                ( self.text_y_margin
                + self.text_height
                + self.text_y_margin
                + self.row_height
                + self.row_y_margin
                )
            + self.bottom_padding
        )
        self.rect = pg.Rect(left_margin, top, self.width, self.height)

        self.ui_manager = ui_manager
        self.panel = pgui.elements.UIPanel(self.rect, manager=self.ui_manager, container=container, object_id="@dark_panel")
        self.rows: list[list[pgui.elements.UITextEntryLine]] = []

        self.texts: list[pgui.elements.UILabel] = []

        current_y = 0
        current_y += self.text_y_margin

        # Drawing

        # Title
        self.texts.append(pgui.elements.UILabel(pg.Rect(self.x_padding, current_y, self.padded_width, self.text_height), title, anchors={"centerx": "centerx"}, parent_element=self.panel, container=self.panel, object_id="@bold_text"))
        current_y += self.text_height
        current_y += self.text_y_margin

        for row_num in range(self.row_count):
            row = []

            # Label
            current_y += self.text_y_margin
            self.texts.append(pgui.elements.UILabel(pg.Rect(self.x_padding, current_y, self.padded_width, self.text_height), row_labels[row_num], self.ui_manager, self.panel, self.panel, anchors={"centerx": "centerx"}))
            current_y += self.text_height
            current_y += self.text_y_margin

            input_width = self.padded_width / self.row_size

            for col_num in range(self.row_size):
                # Input label
                input_label_percent = self.calculate_label_percent(item_labels[row_num][col_num], input_width)
                self.texts.append(pgui.elements.UILabel(pg.Rect(input_width * col_num + self.x_padding, current_y, input_width * input_label_percent, self.row_height), item_labels[row_num][col_num], self.ui_manager, self.panel, self.panel))

                field_width = input_width * (1 - input_label_percent)
                if col_num + 1 != self.row_size:
                    if field_width > 15:
                        field_width -= 10

                # Input field
                row.append(pgui.elements.UITextEntryLine(
                    relative_rect=pg.Rect(
                        input_width * col_num + input_width * input_label_percent + self.x_padding,
                        current_y,
                        field_width,
                        self.row_height
                        ),
                    manager=self.ui_manager,
                    container=self.panel,
                    initial_text=str(default_values[row_num][col_num]),
                    placeholder_text=str(default_values[row_num][col_num])
                    ))

            current_y += self.row_height
            current_y += self.row_y_margin
            self.rows.append(row)

    @staticmethod
    def calculate_label_percent(label_text: str, max_width: float):
        length = len(label_text)
        max_letters = 10
        if length == 0:
            return 0
        elif length > max_letters:
            return 0.9
        else:
            return length / 10

    def destroy(self):
        self.panel.kill()
        for row in self.rows:
            for field in row:
                field.kill()
        for text in self.texts:
            text.kill()

class Hierarchy:
    def __init__(self, rect: pg.Rect, ui_manager: pgui.UIManager, game_objects: list[GameObject]) -> None:
        self.panel = pgui.elements.UIPanel(rect, manager=ui_manager)
        self.rect = rect
        self.ui_manager = ui_manager
        self.game_objects = game_objects
        self.game_object_buttons: dict[pgui.core.UIElement, GameObject] = {}
        self.moving = False
        self.move_button: pgui.elements.UIButton | None = None
        self.largest_x = 0
        self.largest_y = 0
        self.x_scroll = 0
        self.y_scroll = 0
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
        if y > self.largest_y:
            self.largest_y = y

        x += self.x_scroll
        y += self.y_scroll

        if selected_object == game_object:
            selected_button = pgui.elements.UIButton(pg.Rect((x, y), (100, 50)), game_object.name, self.ui_manager, container=self.panel, object_id="@bright_button")
            self.game_object_buttons[selected_button] = game_object
            self.move_button = pgui.elements.UIButton(pg.Rect(x + 100 + 10, y, 50, 50), "", self.ui_manager, self.panel, object_id="@move_button")
        else:
            self.game_object_buttons[pgui.elements.UIButton(pg.Rect((x, y), (100, 50)), game_object.name, self.ui_manager, container=self.panel)] = game_object

        self.y_depth += 1
        for child in game_object.children:
            self.create_buttons(child, selected_object, x_depth + 1)
    
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
    
    def update_y_scroll(self, y_scroll_inc: float):
        new_scroll = y_scroll_inc + self.y_scroll
        max_scroll = self.rect.height - self.largest_y - 70
        if new_scroll <= 0 and new_scroll > max_scroll:
            self.y_scroll = new_scroll
    
    def update_x_scroll(self, x_scroll_inc: float):
        new_scroll = x_scroll_inc + self.x_scroll
        max_scroll = self.rect.width - self.largest_x - 180
        if new_scroll <= 0 and new_scroll > max_scroll:
            self.x_scroll = new_scroll

class Inspector:
    def __init__(self, rect: pg.Rect, ui_manager: pgui.UIManager, game_object: GameObject | None = None) -> None:
        self.game_object = game_object
        self.ui_manager = ui_manager
        self.rect = rect
        self.panel = pgui.elements.UIPanel(rect, manager=ui_manager)

        self.delete_button: pgui.elements.UIButton | None = None
        delete_button_size = 50
        delete_button_padding = 10
        self.delete_button_rect = pg.Rect(self.panel.relative_rect.width - delete_button_padding - delete_button_size, delete_button_padding, delete_button_size, delete_button_size)
        
        self.input_panels: list[InputPanel] = []

    @staticmethod
    def transform_update_function(game_object: GameObject, rows: list[list[pgui.elements.UITextEntryLine]]):
        new_transform = Transform(
            Vec3(float(rows[0][0].text), float(rows[0][1].text), float(rows[0][2].text)),
            Vec3(float(rows[1][0].text), float(rows[1][1].text), float(rows[1][2].text)),
            Vec3(float(rows[2][0].text), float(rows[2][1].text), float(rows[2][2].text))
        )
        game_object.update_transform(new_transform)

    @staticmethod
    def name_update_function(game_object: GameObject, rows: list[list[pgui.elements.UITextEntryLine]]):
        game_object.name = rows[0][0].text

    def set_game_object(self, game_object: GameObject | None):
        self.destroy()
        self.game_object = game_object
        self.create()

    def destroy(self):
            if not self.game_object is None:
                self.delete_button.kill()
                for input_panel in self.input_panels:
                    input_panel.destroy()
                self.input_panels.clear()

    def create(self):
        if self.game_object:

            self.delete_button = pgui.elements.UIButton(self.delete_button_rect, "", self.ui_manager, object_id="@delete_button", container=self.panel)
            
            x_margin = 10
            y_margin = 20
            current_y = self.delete_button.rect.height + y_margin
            # Name panel
            name_panel = InputPanel(
                self.rect.width, x_margin, current_y, [[self.game_object.name]], self.name_update_function, self.panel, self.ui_manager, self.game_object.name, ["Name"], [[""]]
            )
            self.input_panels.append(name_panel)
            current_y += name_panel.height + y_margin

            # Transform panel
            default_values = []
            default_values.append(self.game_object.local_transform.pos.to_list())
            default_values.append(self.game_object.local_transform.scale.to_list())
            default_values.append(self.game_object.local_transform.rotation.to_list())

            row_labels = ["Position", "Scale", "Rotation"]

            item_labels = []
            item_labels.append(["x", "y", "z"])
            item_labels.append(["x", "y", "z"])
            item_labels.append(["x", "y", "z"])

            transform_panel = InputPanel(
                self.rect.width, x_margin, current_y, default_values, self.transform_update_function, self.panel, self.ui_manager, "Transform", row_labels, item_labels
            )

            self.input_panels.append(transform_panel)
            current_y += transform_panel.height + y_margin


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