from main import App
import pygame as pg
import pygame_gui as pgui
import pyrr.matrix44 as mat4
from classes.gameobject import GameObject
from classes.editorcamera import EditorCamera

class Editor(App):
    def __init__(self) -> None:
        super().__init__()

    def init_ui(self):
        self.ui_surface = pg.surface.Surface((self.width, self.height), pg.SRCALPHA)
        self.ui_manager = pgui.UIManager((self.width, self.height))
        self.game_object_buttons: dict[pgui.core.UIElement, GameObject] = {}
        initial_offset = 50
        size = 50
        for i, game_object in enumerate(self.game_objects):
            self.game_object_buttons[pgui.elements.UIButton(pg.Rect((100, initial_offset + size * i), (100, 50)), game_object.name, self.ui_manager)] = game_object
        
        
    def init_variables(self):
        super().init_variables()
        self.viewport = (self.width//4, self.height//4, self.width//2, self.height//2)
        self.camera = EditorCamera(5, 0.01, self.width, self.height, self.viewport)
    
    def main_loop(self):
        running = True
        self.delta_time = self.clock.tick(self.FPS) / 1000
        while running:
            for event in pg.event.get():
                match event.type:
                    case pg.QUIT:
                        running = False
                    case pg.KEYDOWN:
                        if event.key == pg.K_ESCAPE:
                            running = False
                    case pgui.UI_BUTTON_PRESSED:
                        for button in self.game_object_buttons:
                            if event.ui_element == button:
                                print(self.game_object_buttons[button].name)

                self.ui_manager.process_events(event)
            
            self.ui_manager.update(self.delta_time)

            if len(self.game_objects) > 0:
                try:
                    self.renderer.view_matrix = self.camera.get_view_matrix()
                except:
                    self.renderer.view_matrix = mat4.create_identity()
                self.renderer.render_objects(self.game_objects, self.viewport, False)

            # UI
            bg_color = [x * 200 for x in self.renderer.clear_color]
            bg_color[3] = 255
            pg.draw.rect(self.ui_surface, bg_color, pg.Rect(0, 0, self.width, self.height))
            pg.draw.rect(self.ui_surface, (0, 0, 0, 0), pg.Rect(self.viewport[0], self.height - self.viewport[1] - self.viewport[3], self.viewport[2], self.viewport[3]))
            
            self.renderer.render_ui(self.ui_manager, self.ui_surface)
            self.camera.update(self.delta_time)
            self.delta_time = self.clock.tick(self.FPS) / 1000
        self.destroy()


editor = Editor()