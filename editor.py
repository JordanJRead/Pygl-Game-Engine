from main import App
import pygame as pg
import pygame_gui as pgui
import pyrr.matrix44 as mat4
from classes.gameobject import GameObject

class Editor(App):
    def __init__(self) -> None:
        super().__init__()

    def init_ui(self):
        self.ui_manager = pgui.UIManager((self.width, self.height))
        self.game_object_buttons: dict[pgui.core.UIElement, GameObject] = {}
        self.scroll_space = pgui.elements.UIScrollingContainer(pg.Rect(0, 0, self.width//2, self.height))
        self.scroll_space.set_scrollable_area_dimensions((10000, 10000))
        self.game_object_buttons[pgui.elements.UIButton(pg.Rect((350, 275), (100, 50)), self.game_objects[0].name, self.ui_manager, container=self.scroll_space)] = self.game_objects[0]
        
    def init_variables(self):
        super().init_variables()
    
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
                    self.renderer.view_matrix = self.game_objects[0].scripts[0].get_view_matrix()
                except:
                    self.renderer.view_matrix = mat4.create_identity()
                self.renderer.render_objects(self.game_objects, (self.width//2, 0, self.width//2, self.height//2), False)
                self.renderer.render_ui(self.ui_manager)
            self.delta_time = self.clock.tick(self.FPS) / 1000
        self.destroy()

editor = Editor()