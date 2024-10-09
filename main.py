from classes.gameobject import GameObject
from classes.transform import Transform
from classes.rendercomponent import RenderComponent
from classes.vec3 import Vec3
from classes.renderer import Renderer
import classes.transform as transform
from assets.scripts.camera import Camera
import pygame as pg
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

    def init_game_objects(self):
        self.game_objects = self.load_json("gameobjects.json")
        for game_object in self.game_objects:
            self.init_game_object(game_object)

    def load_json(self, path: str):
        # Types
        Vec3Dict = TypedDict('Vec3Dict', {"x": float, "y": float, "z": float})
        TransformDict = TypedDict('TransformDict', {"pos": Vec3Dict, "scale": Vec3Dict, "rot": Vec3Dict})
        RenderDict = TypedDict('RenderDict', {"obj_path": str, "image_path": str})
        ScriptDict = TypedDict('ScriptDict', {"name": str, "args": list[Any]})
        ObjectDict = TypedDict('Object', {"name": str, "transform": TransformDict, "children": Any, "render_component": RenderDict, "scripts": list[ScriptDict]})
        FileDict = TypedDict('FileDict', {"objects": list[ObjectDict]})

        game_objects: list[GameObject] = []

        with open(path) as file:
            json_dict: FileDict = json.load(file)

        for game_object in json_dict["objects"]:
            game_objects.append(self.create_game_object_from_json(game_object))
        return game_objects

    """
    Takes in a game object json dictionary and returns a gameobject with the info from the json put in. Calls itself to create children
    """
    def create_game_object_from_json(self, game_object_dict: dict):
        # Types
        Vec3Dict = TypedDict('Vec3Dict', {"x": float, "y": float, "z": float})
        TransformDict = TypedDict('TransformDict', {"pos": Vec3Dict, "scale": Vec3Dict, "rot": Vec3Dict})
        RenderDict = TypedDict('RenderDict', {"obj_path": str, "image_path": str, "is_bright": int}) # Can be None
        ScriptDict = TypedDict('ScriptDict', {"name": str, "args": list[Any]})
        ObjectDict = TypedDict('Object', {"name": str, "transform": TransformDict, "children": Any, "render_component": RenderDict, "scripts": list[ScriptDict]})

        game_object_dict: ObjectDict = game_object_dict

        # Children
        children_dicts: list[ObjectDict] = game_object_dict["children"]
        children: list[GameObject] = []
        for child_dict in children_dicts:
            children.append(self.create_game_object_from_json(child_dict))

        # Scripts
        scripts = []
        for script_dict in game_object_dict["scripts"]:
            class_ = locate("assets.scripts." + script_dict["name"].lower() + "." + script_dict["name"])
            arguments = script_dict["args"]
            scripts.append((class_, arguments))

        # Render component
        render_component = None
        if game_object_dict["render_component"]:
            render_component = RenderComponent(game_object_dict["render_component"]["obj_path"], game_object_dict["render_component"]["image_path"])
        else:
            render_component = RenderComponent("", "", False)

        game_object = GameObject(
            app=self,
            name=game_object_dict["name"],
            local_transform=Transform(
                Vec3(
                    game_object_dict["transform"]["pos"]["x"],
                    game_object_dict["transform"]["pos"]["y"],
                    game_object_dict["transform"]["pos"]["z"],
                ),
                Vec3(
                    game_object_dict["transform"]["scale"]["x"],
                    game_object_dict["transform"]["scale"]["y"],
                    game_object_dict["transform"]["scale"]["z"],
                ),
                Vec3(
                    game_object_dict["transform"]["rot"]["x"],
                    game_object_dict["transform"]["rot"]["y"],
                    game_object_dict["transform"]["rot"]["z"],
                )
            ),
            children=children,
            render_component= render_component,
            scripts=scripts,
        )
        return game_object
    
    def init_game_object(self, game_object: GameObject):
        for component in game_object.components:
            component.start()
        game_object.local_transform.model_matrix = transform.create_entire_model_matrix(game_object.local_transform, game_object.parent)
        for child in game_object.children:
            self.init_game_object(child)

    def init_ui(self):
        pass
    
    def main_loop(self):
        running = True
        self.delta_time = self.clock.tick(self.FPS) / 1000
        while running:
            # Events
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        running = False

            self.update_game_objects()

            # Rendering
            camera = None
            for game_object in self.game_objects:
                camera: Camera | None = self.get_camera(game_object)
                if camera: break
            if camera:
                self.renderer.render_texture_to_screen(camera.color_texture)

            self.delta_time = self.clock.tick(self.FPS) / 1000

    def update_game_objects(self):
        for game_object in self.game_objects:
            for custom_object in game_object.components:
                custom_object.delta_time = self.delta_time
                custom_object.update()

    """
    Returns the camera component of the gameobject / its children, if it exists
    """
    def get_camera(self, game_object: GameObject):
        camera = game_object.get_component(Camera)
        if not camera:
            for child in game_object.children:
                return self.get_camera(child)
        return camera

    def destroy(self):
        for obj in self.game_objects:
            obj.destroy()
        pg.quit()

if __name__ == "__main__":
    app = App(1920, 1080, 144)