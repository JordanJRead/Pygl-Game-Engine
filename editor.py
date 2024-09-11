from main import App
import pygame as pg
import pygame_gui as pgui
import pyrr.matrix44 as mat4
from classes.gameobject import GameObject
from classes.editorcamera import EditorCamera

class Editor(App):
    def __init__(self, width: int, height: int, FPS: int) -> None:
        super().__init__(width, height, FPS)

    def init_ui(self):
        self.selected_game_object: None | GameObject = None
        self.viewport = (self.width//4, self.height//4, self.width//2, self.height//2)
        self.viewport_rect = pg.Rect(self.viewport[0], self.height - self.viewport[1] - self.viewport[3], self.viewport[2], self.viewport[3])
        self.camera = EditorCamera(5, 0.005, self.width, self.height, self.viewport)

        self.ui_surface = pg.surface.Surface((self.width, self.height), pg.SRCALPHA)
        self.ui_manager = pgui.UIManager((self.width, self.height), "theme.json")
        self.game_object_buttons: dict[pgui.core.UIElement, GameObject] = {}
        initial_offset = 50
        size = 50
        for i, game_object_ui in enumerate(self.ui_game_objects):
            game_object, depth = game_object_ui
            self.game_object_buttons[pgui.elements.UIButton(pg.Rect((100 + 50 * depth, initial_offset + size * i), (100, 50)), game_object.name, self.ui_manager)] = game_object
    
    def select_game_object(self, game_object: GameObject):
        if self.selected_game_object:
            self.selected_game_object.render_component.is_bright = False
        self.selected_game_object = game_object
        game_object.render_component.is_bright = True

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
                    case pg.MOUSEBUTTONDOWN:
                        if event.button == 3:
                            self.camera.prev_mouse_position = pg.mouse.get_pos()
                    case pgui.UI_BUTTON_PRESSED:
                        for button in self.game_object_buttons:
                            if event.ui_element == button:
                                self.select_game_object(self.game_object_buttons[button])

                self.ui_manager.process_events(event)
            
            self.ui_manager.update(self.delta_time)

            if len(self.game_objects) > 0:
                try:
                    self.renderer.view_matrix = self.camera.get_view_matrix()
                except:
                    self.renderer.view_matrix = mat4.create_identity()
                self.renderer.render_objects(self.game_objects, self.viewport, False)

            # UI
            bg_color = (17, 25, 15)
            bg_color = [1.3 * x for x in bg_color]
            pg.draw.rect(self.ui_surface, bg_color, pg.Rect(0, 0, self.width, self.height))
            pg.draw.rect(self.ui_surface, (0, 0, 0, 0), self.viewport_rect)
            
            self.renderer.render_ui(self.ui_manager, self.ui_surface)

            if pg.mouse.get_pressed()[2] and self.viewport_rect.collidepoint(*pg.mouse.get_pos()):
                self.camera.update(self.delta_time)
            self.delta_time = self.clock.tick(self.FPS) / 1000
        self.destroy()


editor = Editor(1920, 1080, 144)