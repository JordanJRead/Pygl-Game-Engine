from classes.gameobject import GameObject
from classes.transform import Transform
from classes.rendercomponent import RenderComponent
from classes import rendercomponent
from classes.vec3 import Vec3
from classes.renderer import Renderer
import pygame as pg
from assets.scripts.playermove import PlayerMove
import pyrr.matrix44 as mat4

class App:
    def __init__(self) -> None:
        self.width = 1920
        self.height = 1080
        self.renderer = Renderer(self.width, self.height)
        self.init_objects()
        self.clock = pg.time.Clock()
        running = True
        self.delta_time = 0
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
            self.delta_time = self.clock.tick(144) / 1000
        self.destroy()

    def init_objects(self):
        # First game object is the camera
        self.game_objects: list[GameObject] = [
            GameObject(
                Transform(Vec3(0, 0, 0), Vec3(1, 1, 1), Vec3(0, 0, 0)), scripts=[PlayerMove(5, 0.01, self.width, self.height)]
            ),
            GameObject(
                Transform(Vec3(0, 0, 5), Vec3(1, 1, 1,), Vec3(0, 0, 0)),
                render_component=RenderComponent("assets/objects/Cube.txt", "assets/images/test.png")
            )
        ]
        self.start_game_objects()
    
    def destroy(self):
        self.end_game_objects()
        for obj in self.game_objects:
            obj.destroy()
        pg.quit()

    def start_game_objects(self):
        for game_object in self.game_objects:
            for script in game_object.scripts:
                script.start()

    def update_game_objects(self):
        for game_object in self.game_objects:
            for script in game_object.scripts:
                script.delta_time = self.delta_time
                script.update()
                
    def end_game_objects(self):
        for game_object in self.game_objects:
            for script in game_object.scripts:
                script.end()
    

if __name__ == "__main__":
    app = App()