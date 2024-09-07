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
    def __init__(self) -> None:
        self.init_variables()
        self.init_game_objects()
        self.init_ui()
        self.main_loop()

    def init_ui(self):
        pass

    def init_variables(self):
        self.width = 1920
        self.height = 1080
        self.FPS = 144
        self.renderer = Renderer(self.width, self.height)
        self.clock = pg.time.Clock()

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
        self.destroy()

    def init_game_objects(self):
        # First game object is the camera
        self.load_json("gameobjects.json")
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
    
    def load_json(self, path: str):
        Vec3Dict = TypedDict('Vec3Dict', {"x": float, "y": float, "z": float})
        TransformDict = TypedDict('TransformDict', {"pos": Vec3Dict, "scale": Vec3Dict, "rot": Vec3Dict})
        RenderDict = TypedDict('RenderDict', {"object_path": str, "image_path": str})
        ScriptDict = TypedDict('ScriptDict', {"name": str, "args": list[Any]})
        ObjectDict = TypedDict('Object', {"name": str, "transform": TransformDict, "parent_name": str, "render_component": RenderDict, "scripts": list[ScriptDict]})
        FileDict = TypedDict('FileDict', {"objects": list[ObjectDict]})
        self.game_objects: list[GameObject] = []
        with open(path) as file:
            json_dict: FileDict = json.load(file)
        for game_object in json_dict["objects"]:
            scripts = []
            for script_dict in game_object["scripts"]:
                class_ = locate("assets.scripts." + script_dict["name"].lower() + "." + script_dict["name"])
                scripts.append(class_(*script_dict["args"]))
            self.game_objects.append(
                GameObject(game_object["name"],
                Transform(
                    Vec3(
                        game_object["transform"]["pos"]["x"],
                        game_object["transform"]["pos"]["y"],
                        game_object["transform"]["pos"]["z"],
                    ),
                    Vec3(
                        game_object["transform"]["scale"]["x"],
                        game_object["transform"]["scale"]["y"],
                        game_object["transform"]["scale"]["z"],
                    ),
                    Vec3(
                        game_object["transform"]["rot"]["x"],
                        game_object["transform"]["rot"]["y"],
                        game_object["transform"]["rot"]["z"],
                    )
                ),
                game_object["parent_name"],
                RenderComponent(
                    game_object["render_component"]["object_path"],
                    game_object["render_component"]["image_path"]
                ),
                scripts
            ))

if __name__ == "__main__":
    app = App()