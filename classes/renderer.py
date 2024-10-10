import pygame as pg
import pygame_gui as pgui
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
from classes.gameobject import GameObject
from classes.rendercomponent import RenderComponent
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
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        self.shader = self.create_shader("shaders/vertex.glsl", "shaders/fragment.glsl")
        glUseProgram(self.shader)
        glUniform1i(glGetUniformLocation(self.shader, "tex"), 0)

        self.quad_shader = self.create_shader("shaders/tex_vertex.glsl", "shaders/tex_fragment.glsl")
        glUniform1i(glGetUniformLocation(self.quad_shader, "tex"), 0)

        self.quad_vertices = [
            # Top right
            -1, 1, 0, 0, 1,
            1, 1, 0, 1, 1,
            1, -1, 0, 1, 0,

            # Bottom left
            1, -1, 0, 1, 0,
            -1, -1, 0, 0, 0,
            -1, 1, 0, 0, 1
        ]

        self.quad_vertices = np.array(self.quad_vertices, dtype=np.float32)
        vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, vbo)
        glBufferData(GL_ARRAY_BUFFER, self.quad_vertices.nbytes, self.quad_vertices, GL_STATIC_DRAW)

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 5 * 4, ctypes.c_void_p(0))
        
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 5 * 4, ctypes.c_void_p(3 * 4))
    
    def render_objects_to_fbo(self, objects: list[GameObject], projection_matrix, view_matrix, fbo: int = 0, viewport: tuple[int, int, int, int] | None = None, flip = True, default_render_component: RenderComponent | None = None):
        # Frame setup
        glUseProgram(self.shader)
        glUniformMatrix4fv(glGetUniformLocation(self.shader, "viewMatrix"), 1, GL_FALSE, view_matrix)
        glUniformMatrix4fv(glGetUniformLocation(self.shader, "projectionMatrix"), 1, GL_TRUE, projection_matrix)
        glBindFramebuffer(GL_FRAMEBUFFER, fbo)
        if viewport == None:
            viewport = (0, 0, self.width, self.height)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glUseProgram(self.shader)
        glViewport(*viewport)

        for object in objects:
            self.render_object(object, default_render_component)
        if flip:
            pg.display.flip()
        
        viewport = (0, 0, self.width, self.height)
        glViewport(*viewport)

    def render_object(self, object: GameObject, default_render_component: RenderComponent | None = None):
            if object.render_component.is_active or default_render_component:
                if not object.render_component.is_active:
                    vao = default_render_component.vao
                    texture2d = default_render_component.texture2d
                    vertices = default_render_component.vertices
                else:
                    vao = object.render_component.vao
                    texture2d = object.render_component.texture2d
                    vertices = object.render_component.vertices
                glUniformMatrix4fv(glGetUniformLocation(self.shader, "modelMatrix"), 1, GL_FALSE, object.local_transform.model_matrix)
                glUniform1i(glGetUniformLocation(self.shader, "isBright"), object.render_component.is_bright)
                texture2d.use()
                glBindVertexArray(vao)
                glDrawArrays(GL_TRIANGLES, 0, len(vertices))
            for child in object.children:
                self.render_object(child, default_render_component)
    
    def render_texture_to_screen(self, texture: int, clear=True):
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        if clear:
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glBindTexture(GL_TEXTURE_2D, texture)
        glUseProgram(self.quad_shader)
        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLES, 0, 6)
        pg.display.flip()

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