from classes.gameobject import GameObject
from classes.transform import Transform
from classes.rendercomponent import RenderComponent
from classes.vec3 import Vec3
from classes.editorrenderer import EditorRenderer
import pygame as pg
import importlib
script_classes = importlib.import_module("assets.scripts")
import pyrr.matrix44 as mat4
import json
from typing import TypedDict
from typing import Any

class Editor:
    def __init__(self) -> None:
        self.init_renderer(self)
        self.init_game_objects(self)
        running = True
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
                self.renderer.render_objects(self.game_objects)
        pg.quit()
    
    def init_renderer(self):
        self.width = 1920
        self.height = 1080
        self.renderer = EditorRenderer(self.width, self.height)

    def init_game_objects(self):
        self.load_json("gameobjects.json")
        for game_object in self.game_objects:
            game_object.init_parent(self.game_objects)
            for script in game_object.scripts:
                script.start()

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
                class_ = getattr(script_classes, script_dict["name"])
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

editor = Editor()