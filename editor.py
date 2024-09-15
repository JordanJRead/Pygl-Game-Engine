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

class Editor(App):
    def __init__(self, width: int, height: int, FPS: int) -> None:
        super().__init__(width, height, FPS)

    def init_ui(self):
        self.window_name = "Editor"
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
                            pg.display.set_caption("*" + self.window_name)
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
        # with open(path, "r") as file:
        pass


editor = Editor(1920, 1080, 144)