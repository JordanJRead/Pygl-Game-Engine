from main import App
import pygame as pg
import pygame_gui as pgui
import pyrr.matrix44 as mat4
from classes.gameobject import GameObject
from classes.editorcamera import EditorCamera
from classes.uiutils import Colors, UISettings
from OpenGL.GL import *

class Editor(App):
    def __init__(self, width: int, height: int, FPS: int) -> None:
        super().__init__(width, height, FPS)

    def init_ui(self):
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
        # self.ui_settings = UISettings(
        #                               hierarchy_rect=pg.Rect(40, 40, self.width / 6.4, self.height - 75),
        #                               hierarchy_color=self.colors.light_green,
        #                               inspector_rect=pg.Rect(self.width - 40 - self.width / 6.4, 40, self.width / 6.4, self.height -75),
        #                               inspector_color=self.colors.light_green
        #                               )

        self.ui_surface = pg.surface.Surface((self.width, self.height), pg.SRCALPHA)
        self.ui_manager = pgui.UIManager((self.width, self.height), "theme.json")

        # Hierarchy
        hierarchy_rect = pg.Rect(40, 40, self.width / 6.4, self.height - 75)
        self.hierarchy_panel = pgui.elements.UIPanel(hierarchy_rect, manager=self.ui_manager)
        self.game_object_buttons: dict[pgui.core.UIElement, GameObject] = {}

        self.top_margin = 10
        self.left_margin = 10
        self.size = 50
        self.depth_offset = 50

        self.y_depth = 0
        for game_object in self.game_objects:
            self.create_buttons(game_object, self.y_depth)
        
        # Inspector
        inspector_rect = pg.Rect(self.width - 40 - self.width / 6.4, 40, self.width / 6.4, self.height -75)
        self.inspector_panel = pgui.elements.UIPanel(inspector_rect, manager=self.ui_manager)
        self.object_name = pgui.elements.UITextEntryLine(pg.Rect(0, 0, 100, 50), self.ui_manager, self.inspector_panel, anchors={"centerx": "centerx"}, placeholder_text="hello")
    
    def create_buttons(self, game_object: GameObject, y_depth, x_depth: int = 0):
        x = self.left_margin + self.depth_offset * x_depth
        y = self.top_margin + self.size * y_depth
        self.game_object_buttons[pgui.elements.UIButton(pg.Rect((x, y), (100, 50)), game_object.name, self.ui_manager, container=self.hierarchy_panel)] = game_object
        self.y_depth += 1
        for child in game_object.children:
            self.create_buttons(child, self.y_depth, x_depth + 1)

    def select_game_object(self, game_object: GameObject):
        if self.selected_game_object:
            self.selected_game_object.render_component.is_bright = False
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
                        for button in self.game_object_buttons:
                            if event.ui_element == button:
                                self.select_game_object(self.game_object_buttons[button])
                self.ui_manager.process_events(event)
            
            self.ui_manager.update(self.delta_time)

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

editor = Editor(1920, 1080, 144)