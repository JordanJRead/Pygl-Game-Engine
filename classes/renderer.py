import pygame as pg
import pygame_gui as pgui
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
from classes.gameobject import GameObject
import pyrr.matrix44 as mat4
import numpy as np
from math import tan, radians

class Renderer:
    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        pg.init()
        self.screen = pg.display.set_mode((width, height), pg.OPENGL|pg.DOUBLEBUF).convert_alpha()
        self.clear_color = (0.4, 0.4, 0.4, 1)
        glClearColor(*self.clear_color)
        glActiveTexture(GL_TEXTURE0)
        glEnable(GL_DEPTH_TEST)
        self.shader = self.create_shader("shaders/vertex.glsl", "shaders/fragment.glsl")
        glUseProgram(self.shader)
        glUniform1i(glGetUniformLocation(self.shader, "tex"), 0)
        glUniformMatrix4fv(glGetUniformLocation(self.shader, "projectionMatrix"), 1, GL_TRUE, self.get_projection_matrix(0.1, 100000, width/height, 90))
        self.view_matrix = mat4.create_identity()

        self.pg_shader = self.create_shader("shaders/pg_vertex.glsl", "shaders/pg_fragment.glsl")
        glUniform1i(glGetUniformLocation(self.pg_shader, "tex"), 0)

        self.pg_quad_vertices = [
            # Top right
            -1, 1, 0, 0, 0,
            1, 1, 0, 1, 0,
            1, -1, 0, 1, 1,

            # Bottom left
            1, -1, 0, 1, 1,
            -1, -1, 0, 0, 1,
            -1, 1, 0, 0, 0
        ]

        self.pg_quad_vertices = np.array(self.pg_quad_vertices, dtype=np.float32)
        pg_vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, pg_vbo)
        glBufferData(GL_ARRAY_BUFFER, self.pg_quad_vertices.nbytes, self.pg_quad_vertices, GL_STATIC_DRAW)

        self.pg_vao = glGenVertexArrays(1)
        glBindVertexArray(self.pg_vao)
        
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 5 * 4, ctypes.c_void_p(0))
        
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 5 * 4, ctypes.c_void_p(3 * 4))
    
    def render_objects(self, objects: list[GameObject], viewport = None, flip = True):
        if viewport == None:
            viewport = (0, 0, self.width, self.height)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glUseProgram(self.shader)
        glViewport(*viewport)
        glUniformMatrix4fv(glGetUniformLocation(self.shader, "viewMatrix"), 1, GL_FALSE, self.view_matrix)
        for obj in objects:
            if obj.render_component.active:
                glUniformMatrix4fv(glGetUniformLocation(self.shader, "modelMatrix"), 1, GL_FALSE, obj.render_component.model_matrix)
                obj.render_component.texture2d.use()
                glBindVertexArray(obj.render_component.vao)
                glDrawArrays(GL_TRIANGLES, 0, len(obj.render_component.vertices))
        if flip:
            pg.display.flip()

    def render_ui(self, ui_manager: pgui.UIManager, ui_surface: pg.Surface):
        ui_manager.draw_ui(ui_surface)
        pg_texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, pg_texture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self.width, self.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, pg.image.tobytes(ui_surface, "RGBA"))
        glUseProgram(self.pg_shader)
        glDisable(GL_DEPTH_TEST)
        glBindVertexArray(self.pg_vao)
        glViewport(0, 0, self.width, self.height)
        glDrawArrays(GL_TRIANGLES, 0, 6)

        pg.display.flip()
        
        glDeleteTextures(1, (pg_texture,))
        glEnable(GL_DEPTH_TEST)
    
    def create_shader(self, vertex_path: str, fragment_path: str):
        vertex_src = ""
        with open(vertex_path) as vertex_file:
            vertex_src = vertex_file.readlines()
        
        fragment_src = ""
        with open(fragment_path) as fragment_file:
            fragment_src = fragment_file.readlines()
        
        shader = compileProgram(
            compileShader(vertex_src, GL_VERTEX_SHADER),
            compileShader(fragment_src, GL_FRAGMENT_SHADER)
        )

        return shader
    
    def get_projection_matrix(self, near_distance, far_distance, aspect_ratio, horizontal_fov_deg):
        width = near_distance*tan(radians(horizontal_fov_deg / 2))
        height = width / aspect_ratio

        a = (near_distance + far_distance) / (far_distance - near_distance)
        b = (-2 * far_distance * near_distance) / (far_distance - near_distance)

        projection = np.array([
            [near_distance / width, 0,                           0, 0],
            [0,                          near_distance / height, 0, 0],
            [0,                          0,                           a, b],
            [0,                          0,                           1, 0]
        ], dtype=np.float32)

        return projection