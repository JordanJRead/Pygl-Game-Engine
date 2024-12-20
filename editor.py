from main import App
import pygame as pg
import pygame_gui as pgui
from classes.gameobject import GameObject
from classes.editorcamera import EditorCamera
from classes.rendercomponent import RenderComponent
from classes.colors import Colors
from classes.editoritems import *
from OpenGL.GL import *
from typing import TypedDict
from typing import Any
import json
from classes import raytracing
from math import tan, radians
from pathlib import Path
import pyperclip
# TODO clean up hierarchy code
class Editor(App):
    def __init__(self, width: int, height: int, FPS: int) -> None:
        super().__init__(width, height, FPS)

    def init_ui(self):
        self.default_render_component = RenderComponent("assets/objects/Default.obj", "assets/images/grey.png")
        self.window_name = "Editor"
        self.unsaved_window_name = "*Editor"
        self.is_saved = True
        pg.display.set_caption(self.window_name)
        self.viewport = (self.width//4, self.height//4, self.width//2, self.height//2)
        self.viewport_rect = pg.Rect(self.viewport[0], self.height - self.viewport[1] - self.viewport[3], self.viewport[2], self.viewport[3])

        self.selected_game_object: None | GameObject = None
        self.camera = EditorCamera(5, 0.005, self.width, self.height, self.viewport, 0.1, 10000, 90, self.width/self.height)
        self.is_moving = False

        # UI Texture
        self.ui_texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.ui_texture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)

        # Setting up
        self.colors = Colors()
        self.ui_surface = pg.surface.Surface((self.width, self.height), pg.SRCALPHA)
        self.ui_manager = pgui.UIManager((self.width, self.height), "theme.json")

        element_width_percent = 0.2
        element_padding = 25
        element_top_padding = 50

        element_width = self.width * element_width_percent

        # Hierarchy
        hierarchy_rect = pg.Rect(element_padding, element_padding + element_top_padding, element_width, self.height - element_padding * 2 - element_top_padding)
        self.hierarchy =  Hierarchy(hierarchy_rect, self.ui_manager, self.game_objects)

        # Inspector
        inspector_rect = pg.Rect(self.width - element_padding - element_width, element_padding, element_width, self.height - element_padding * 2)
        self.inspector = Inspector(inspector_rect, self.ui_manager)

        # Create buttons
        self.creation_buttons = CreationButtons(self.hierarchy.rect, self.ui_manager)

        # File display
        file_display_y_padding = 25
        file_display_rect = pg.Rect(self.viewport_rect.left, self.viewport_rect.bottom + file_display_y_padding, self.viewport_rect.width, self.height - file_display_y_padding * 2 - self.viewport_rect.bottom)
        self.file_display = FileDisplay(file_display_rect, self.ui_manager, "./assets")

    def select_game_object(self, game_object: GameObject):
        if game_object is None:
            game_object = self.selected_game_object # Deselect
        self.inspector.set_game_object(game_object)

        # Disable
        if self.selected_game_object:
            self.selected_game_object.render_component.is_bright = False

        # Deselect
        if self.selected_game_object == game_object:
            self.creation_buttons.disable_child_button()
            self.selected_game_object = None
            self.inspector.set_game_object(None)
            self.hierarchy.build(None)
            return

        # Set new
        self.creation_buttons.enable_child_button()
        self.selected_game_object = game_object
        game_object.render_component.is_bright = True
        self.hierarchy.build(self.selected_game_object)

    def main_loop(self):
        self.running = True
        self.delta_time = self.clock.tick(self.FPS) / 1000
        while self.running:
            keys = pg.key.get_pressed()
            if keys[pg.K_s] and keys[pg.K_LCTRL]:
                self.save()
            self.check_events(keys)

            self.ui_manager.update(self.delta_time)
            self.ui_manager.rebuild_all_from_changed_theme_data()

            # Render scene
            self.renderer.render_objects_to_fbo(
                objects=self.game_objects,
                projection_matrix=self.camera.projection_matrix,
                view_matrix=self.camera.get_view_matrix(),
                fbo=0,
                viewport=self.viewport,
                flip=False,
                default_render_component=self.default_render_component
                )
            
            # UI
            pg.draw.rect(self.ui_surface, self.colors.dark_green, pg.Rect(0, 0, self.width, self.height))
            pg.draw.rect(self.ui_surface, (0, 0, 0, 0), self.viewport_rect)

            self.ui_manager.draw_ui(self.ui_surface)
            self.ui_surface = pg.transform.flip(self.ui_surface, False, True)

            glBindTexture(GL_TEXTURE_2D, self.ui_texture)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self.width, self.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, pg.image.tobytes(self.ui_surface, "RGBA"))

            self.renderer.render_texture_to_screen(self.ui_texture, False)

            # Move
            if self.is_moving:
                self.camera.update(self.delta_time)
            self.delta_time = self.clock.tick(self.FPS) / 1000

    def dir_from_pixels(self, pos):
        distance_from_center = [pos[0] - self.viewport_rect.centerx, pos[1] - self.viewport_rect.centery]
        result = Vec3(
            distance_from_center[0], -distance_from_center[1], self.viewport_rect.width / 2 / tan(radians(self.camera.horizontal_fov_deg / 2))
        )
        return result

    def check_events(self, keys):
        for event in pg.event.get():
            match event.type:

                # Closing
                case pg.QUIT:
                    #if self.is_saved:
                    self.running = False
                case pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:# and self.is_saved:
                        self.running = False
                    # Delete
                    if event.key == pg.K_DELETE:
                        if self.selected_game_object:
                            self.delete_selected_object()
                            self.unsave()

                # Move in scene
                case pg.MOUSEBUTTONDOWN:

                    # Select object with raycasting
                    if event.button == 1 and self.viewport_rect.collidepoint(pg.mouse.get_pos()):
                        self.select_game_object(raytracing.ray_cast_game_objects(Vec3.zero(), self.dir_from_pixels(pg.mouse.get_pos()), self.game_objects, self.camera.get_view_matrix(), self.default_render_component))

                    if event.button == 3 and self.viewport_rect.collidepoint(pg.mouse.get_pos()):
                        self.camera.prev_mouse_position = pg.mouse.get_pos()
                        self.is_moving = True
                case pg.MOUSEBUTTONUP:
                    if event.button == 3:
                        self.is_moving = False

                # Scrolling
                case pg.MOUSEWHEEL:
                    hovered_object: ScrollableContainer | None = None
                    if pg.Rect.collidepoint(self.hierarchy.rect, pg.mouse.get_pos()):
                        hovered_object = self.hierarchy
                    if pg.Rect.collidepoint(self.inspector.rect, pg.mouse.get_pos()):
                        hovered_object = self.inspector
                    if pg.Rect.collidepoint(self.file_display.rect, pg.mouse.get_pos()):
                        hovered_object = self.file_display
                    if hovered_object:
                        if keys[pg.K_LSHIFT]:
                            hovered_object.update_x_scroll(event.y * 200)
                        else:
                            hovered_object.update_y_scroll(event.y * 20)
                        hovered_object.build(self.selected_game_object)
                
                # Buttons
                case pgui.UI_BUTTON_PRESSED:
                    
                    # File display
                    for folder_button in self.file_display.folder_buttons:
                        if event.ui_element == folder_button:
                            self.file_display.current_path = Path(self.file_display.folder_buttons[folder_button])
                            self.file_display.build()
                    for file_button in self.file_display.file_buttons:
                        if event.ui_element == file_button:
                            pyperclip.copy(self.file_display.file_buttons[file_button])

                    # Hierarchy
                    for button in self.hierarchy.game_object_buttons:
                        if event.ui_element == button:

                            # Move object in hierarchy to clicked on object
                            if self.hierarchy.moving:
                                self.unsave()
                                new_parent = self.hierarchy.game_object_buttons[button]
                                if new_parent in self.selected_game_object.children: # Swap parent and child (not implemented)
                                    pass
                                else:
                                    new_parent.add_child(self.selected_game_object, 0)
                                    self.selected_game_object.update_transform(self.selected_game_object.local_transform)
                                    self.hierarchy.build(self.selected_game_object)
                                    self.hierarchy.toggle_move_button()
                            else:
                                # Select game object
                                self.select_game_object(self.hierarchy.game_object_buttons[button])
                            break
                    
                    # Delete component
                    for input_panel in self.inspector.input_panels:
                        if event.ui_element == input_panel.delete_button:
                            input_panel.delete_function(self.inspector.game_object, input_panel.rows, input_panel.func_data)
                            self.inspector.build(self.inspector.game_object)
                            self.inspector.update_y_scroll(0)

                    match event.ui_element:
                        # Create object
                        case self.creation_buttons.create_top_level_button:
                            new_object = GameObject(self, "New Object")
                            self.game_objects.append(new_object)
                            self.select_game_object(new_object)
                            self.unsave()
                        
                        # Create child
                        case self.creation_buttons.child_button:
                            if self.selected_game_object:
                                new_object = GameObject(self, "New Child Object")
                                self.selected_game_object.add_child(new_object, 0)
                                self.select_game_object(new_object)
                                self.unsave()

                        # Delete object
                        case self.inspector.delete_button:
                            self.delete_selected_object()

                        # Toggle moving
                        case self.hierarchy.move_button:
                            self.hierarchy.toggle_move_button()

                case pgui.UI_TEXT_ENTRY_FINISHED:
                    # Set value in inspector
                    for input_panel in self.inspector.input_panels:
                        for row in input_panel.rows:
                            for input_field in row:
                                if event.ui_element == input_field:
                                    input_panel.function(self.inspector.game_object, input_panel.rows, input_panel.func_data)
                                    self.hierarchy.build()
                                    self.inspector.set_game_object(self.selected_game_object) # Refresh
                                    self.unsave()
                                    break

            self.ui_manager.process_events(event)

    def delete_selected_object(self):
        if self.selected_game_object:
            game_object_to_destroy = self.selected_game_object
            self.select_game_object(self.selected_game_object)
            game_object_to_destroy.destroy()
            self.hierarchy.build(self.selected_game_object)
            if game_object_to_destroy.parent is not None:
                self.select_game_object(game_object_to_destroy.parent)
            self.unsave()

    def save(self, path: str = "gameobjects.json"):
        self.is_saved = True
        pg.display.set_caption(self.window_name)
        # Types
        Vec3Dict = TypedDict('Vec3Dict', {"x": float, "y": float, "z": float})
        TransformDict = TypedDict('TransformDict', {"pos": Vec3Dict, "scale": Vec3Dict, "rot": Vec3Dict})
        RenderDict = TypedDict('RenderDict', {"obj_path": str, "image_path": str})
        ScriptDict = TypedDict('ScriptDict', {"name": str, "args": list[Any]})
        ObjectDict = TypedDict('Object', {"name": str, "transform": TransformDict, "children": Any, "render_component": RenderDict, "scripts": list[ScriptDict]})

        game_object_dicts: list[ObjectDict] = []

        for game_object in self.game_objects:
            game_object_dicts.append(self.create_dict_from_game_object(game_object))

        with open(path, "w") as file:
            json.dump({"objects": game_object_dicts}, file, indent=2)
    
    def unsave(self):
        self.is_saved = False
        pg.display.set_caption(self.unsaved_window_name)

    def create_dict_from_game_object(self, game_object: GameObject):
        # Types
        Vec3Dict = TypedDict('Vec3Dict', {"x": float, "y": float, "z": float})
        TransformDict = TypedDict('TransformDict', {"pos": Vec3Dict, "scale": Vec3Dict, "rot": Vec3Dict})
        RenderDict = TypedDict('RenderDict', {"obj_path": str, "image_path": str})
        ScriptDict = TypedDict('ScriptDict', {"name": str, "args": list[Any]})
        ObjectDict = TypedDict('Object', {"name": str, "transform": TransformDict, "children": Any, "render_component": RenderDict, "scripts": list[ScriptDict]})
        FileDict = TypedDict('FileDict', {"objects": list[ObjectDict]})

        # Transform
        transform_dict: TransformDict = {
            "pos": {"x": game_object.local_transform.pos.x, "y": game_object.local_transform.pos.y, "z": game_object.local_transform.pos.z},
            "rot": {"x": game_object.local_transform.rotation.x, "y": game_object.local_transform.rotation.y, "z": game_object.local_transform.rotation.z},
            "scale": {"x": game_object.local_transform.scale.x, "y": game_object.local_transform.scale.y, "z": game_object.local_transform.scale.z}}

        # Scripts
        script_dict_list: list[ScriptDict] = []
        for script in game_object.script_data:
            script_dict: ScriptDict = {"name": script[0].__name__, "args": script[1]}
            script_dict_list.append(script_dict)

        # Children
        child_dicts: list[ObjectDict] = []
        for child in game_object.children:
            child_dicts.append(self.create_dict_from_game_object(child))

        # Render component
        render_component_dict: RenderDict | None = None
        if game_object.render_component.is_active:
            render_component_dict = {"obj_path": game_object.render_component.obj_path, "image_path": game_object.render_component.image_path}

        game_object_dict: ObjectDict = {}
        game_object_dict["name"] = game_object.name
        game_object_dict["transform"] = transform_dict
        game_object_dict["children"] = child_dicts
        game_object_dict["render_component"] = render_component_dict
        game_object_dict["scripts"] = script_dict_list

        return game_object_dict

if __name__ == "__main__":
    editor = Editor(1920, 1080, 144)