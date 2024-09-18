from main import App
import pygame as pg
import pygame_gui as pgui
import pyrr.matrix44 as mat4
from classes.gameobject import GameObject
from classes.editorcamera import EditorCamera
from classes.colors import Colors
from classes.inspector import Inspector
from classes.hierarchy import Hierarchy
from OpenGL.GL import *
from typing import TypedDict
from typing import Any
import json

class Editor(App):
    def __init__(self, width: int, height: int, FPS: int) -> None:
        super().__init__(width, height, FPS)

    def init_ui(self):
        self.window_name = "Editor"
        self.unsaved_window_name = "*Editor"
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

        # Hierarchy
        hierarchy_rect = pg.Rect(40, 40, self.width / 6.4, self.height - 75)
        self.hierarchy =  Hierarchy(hierarchy_rect, self.ui_manager, self.game_objects)

        # Inspector
        inspector_rect = pg.Rect(self.width - 40 - self.width / 6.4, 40, self.width / 6.4, self.height -75)
        self.inspector = Inspector(inspector_rect, self.ui_manager)

    def select_game_object(self, game_object: GameObject):
        if self.selected_game_object:
            self.selected_game_object.render_component.is_bright = False

        if self.selected_game_object == game_object:
            self.selected_game_object = None
            self.inspector.set_game_object(None)
            return
        self.inspector.set_game_object(game_object)
        self.selected_game_object = game_object
        game_object.render_component.is_bright = True

    def main_loop(self):
        running = True
        self.delta_time = self.clock.tick(self.FPS) / 1000
        while running:
            # Events
            for event in pg.event.get():
                match event.type:
                    case pg.QUIT:
                        running = False
                    case pg.KEYDOWN:
                        if event.key == pg.K_ESCAPE:
                            running = False
                        elif event.key == pg.K_s:
                            self.save()
                    case pg.MOUSEBUTTONDOWN:
                        if event.button == 3 and self.viewport_rect.collidepoint(*pg.mouse.get_pos()):
                            self.camera.prev_mouse_position = pg.mouse.get_pos()
                            self.is_moving = True
                    case pg.MOUSEBUTTONUP:
                        if event.button == 3:
                            self.is_moving = False
                    case pgui.UI_BUTTON_PRESSED:
                        for button in self.hierarchy.game_object_buttons:
                            if event.ui_element == button:
                                self.select_game_object(self.hierarchy.game_object_buttons[button])
                    
                    # Change game object name
                    case pgui.UI_TEXT_ENTRY_FINISHED:
                        if event.ui_object_id == "panel." + self.inspector.ui_id:
                            self.selected_game_object.name = event.text
                            self.hierarchy.game_objects = self.game_objects
                            self.hierarchy.build_buttons()
                            pg.display.set_caption(self.unsaved_window_name)
                self.ui_manager.process_events(event)
            
            self.ui_manager.update(self.delta_time)
            self.ui_manager.rebuild_all_from_changed_theme_data()

            # Render scene
            self.renderer.render_objects_to_fbo(
                objects=self.game_objects,
                projection_matrix=self.camera.projection_matrix,
                view_matrix=self.camera.get_view_matrix(),
                fbo=0,
                viewport=self.viewport,
                flip=False
                )
            
            # UI
            pg.draw.rect(self.ui_surface, self.colors.dark_green, pg.Rect(0, 0, self.width, self.height))
            pg.draw.rect(self.ui_surface, (0, 0, 0, 0), self.viewport_rect)

            self.ui_manager.draw_ui(self.ui_surface)
            self.ui_surface = pg.transform.flip(self.ui_surface, False, True)

            glBindTexture(GL_TEXTURE_2D, self.ui_texture)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self.width, self.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, pg.image.tobytes(self.ui_surface, "RGBA"))

            self.renderer.render_texture_to_quad(self.ui_texture, False)

            # Move
            if self.is_moving:
                self.camera.update(self.delta_time)
            self.delta_time = self.clock.tick(self.FPS) / 1000

    def save(self, path: str = "gameobjects.json"):
        pg.display.set_caption(self.window_name)
        # Types
        Vec3Dict = TypedDict('Vec3Dict', {"x": float, "y": float, "z": float})
        TransformDict = TypedDict('TransformDict', {"pos": Vec3Dict, "scale": Vec3Dict, "rot": Vec3Dict})
        RenderDict = TypedDict('RenderDict', {"obj_path": str, "image_path": str})
        ScriptDict = TypedDict('ScriptDict', {"name": str, "args": list[Any]})
        ObjectDict = TypedDict('Object', {"name": str, "transform": TransformDict, "children": Any, "render_component": RenderDict, "scripts": list[ScriptDict]})
        FileDict = TypedDict('FileDict', {"objects": list[ObjectDict]})

        game_object_dicts: list[ObjectDict] = []

        for game_object in self.game_objects:
            game_object_dicts.append(self.create_dict_from_game_object(game_object))

        with open(path, "w") as file:
            json.dump({"objects": game_object_dicts}, file)
    
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
        for script in game_object.scripts:
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


editor = Editor(1920, 1080, 144)