from classes.gameobject import GameObject
from classes.transform import Transform
from classes.rendercomponent import RenderComponent
from classes.vec3 import Vec3
from classes.renderer import Renderer
import pygame as pg
import pyrr.matrix44 as mat4
import json
from typing import TypedDict
from typing import Any
from pydoc import locate

# Required to run on my Crostini Linux virtual machine
import os
os.environ["SDL_VIDEO_X11_FORCE_EGL"] = "1"
class App:
    def __init__(self, width: int, height: int, FPS: int) -> None:
        self.width = width
        self.height = height
        self.FPS = FPS
        self.renderer = Renderer(self.width, self.height)
        self.clock = pg.time.Clock()
        self.init_game_objects()
        self.init_ui()
        self.main_loop()
        self.destroy()

    def init_ui(self):
        pass
    
    def main_loop(self):
        running = True
        self.delta_time = self.clock.tick(self.FPS) / 1000
        while running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        running = False
            if len(self.game_objects) > 0:
                try:
                    self.renderer.view_matrix = self.game_objects[0].scripts[0].get_view_matrix()
                except:
                    self.renderer.view_matrix = mat4.create_identity()
                self.update_game_objects()
                self.renderer.render_objects(self.game_objects)
            self.delta_time = self.clock.tick(self.FPS) / 1000

    def init_game_objects(self):
        # First game object is the camera
        self.game_objects, self.ui_game_objects = self.load_json("gameobjects.json")
        for game_object in self.game_objects:
            game_object.init_parent(self.game_objects)
            for script in game_object.scripts:
                script.app = self
                script.start()
    
    def destroy(self):
        for obj in self.game_objects:
            obj.destroy()
        pg.quit()

    def update_game_objects(self):
        for game_object in self.game_objects:
            for script in game_object.scripts:
                script.delta_time = self.delta_time
                script.update()

    def create_game_object_from_json(self, game_object_json: dict, game_objects: list[GameObject], ui_game_objects: list[tuple[GameObject, int]], depth: int = 0, parent_name: str = ""):
        Vec3Dict = TypedDict('Vec3Dict', {"x": float, "y": float, "z": float})
        TransformDict = TypedDict('TransformDict', {"pos": Vec3Dict, "scale": Vec3Dict, "rot": Vec3Dict})
        RenderDict = TypedDict('RenderDict', {"object_path": str, "image_path": str, "is_bright": int})
        ScriptDict = TypedDict('ScriptDict', {"name": str, "args": list[Any]})
        ObjectDict = TypedDict('Object', {"name": str, "transform": TransformDict, "children": Any, "render_component": RenderDict, "scripts": list[ScriptDict]})

        scripts = []
        game_object_json: ObjectDict = game_object_json
        for script_dict in game_object_json["scripts"]:
            class_ = locate("assets.scripts." + script_dict["name"].lower() + "." + script_dict["name"])
            scripts.append(class_(*script_dict["args"]))
        game_object = GameObject(game_object_json["name"],
            Transform(
                Vec3(
                    game_object_json["transform"]["pos"]["x"],
                    game_object_json["transform"]["pos"]["y"],
                    game_object_json["transform"]["pos"]["z"],
                ),
                Vec3(
                    game_object_json["transform"]["scale"]["x"],
                    game_object_json["transform"]["scale"]["y"],
                    game_object_json["transform"]["scale"]["z"],
                ),
                Vec3(
                    game_object_json["transform"]["rot"]["x"],
                    game_object_json["transform"]["rot"]["y"],
                    game_object_json["transform"]["rot"]["z"],
                )
            ),
            parent_name,
            RenderComponent(
                game_object_json["render_component"]["object_path"],
                game_object_json["render_component"]["image_path"]
            ),
            scripts
        )
        game_objects.append(game_object)
        ui_game_objects.append(
            (game_object, depth)
        )
        for child in game_object_json["children"]:
            child: ObjectDict = child
            self.create_game_object_from_json(child, game_objects, ui_game_objects, depth + 1, game_object_json["name"])

        return game_objects, ui_game_objects

    def load_json(self, path: str):
        Vec3Dict = TypedDict('Vec3Dict', {"x": float, "y": float, "z": float})
        TransformDict = TypedDict('TransformDict', {"pos": Vec3Dict, "scale": Vec3Dict, "rot": Vec3Dict})
        RenderDict = TypedDict('RenderDict', {"object_path": str, "image_path": str})
        ScriptDict = TypedDict('ScriptDict', {"name": str, "args": list[Any]})
        ObjectDict = TypedDict('Object', {"name": str, "transform": TransformDict, "children": Any, "render_component": RenderDict, "scripts": list[ScriptDict]})
        FileDict = TypedDict('FileDict', {"objects": list[ObjectDict]})
        game_objects: list[GameObject] = []
        ui_game_objects: list[tuple[GameObject, int]] = []
        with open(path) as file:
            json_dict: FileDict = json.load(file)
        for game_object in json_dict["objects"]:
            game_objects, ui_game_objects = self.create_game_object_from_json(game_object, game_objects, ui_game_objects)
        return game_objects, ui_game_objects

    def search_game_objects(self, name: str):
        for game_object in self.game_objects:
            if game_object.name == name:
                return game_object
        return None

if __name__ == "__main__":
    app = App(1920, 1080, 144)