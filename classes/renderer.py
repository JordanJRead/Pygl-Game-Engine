import pygame as pg
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
from classes.gameobject import GameObject
import numpy as np
from math import radians, tan
import pyrr.matrix44 as mat4

class Renderer:
    def __init__(self, width: int, height: int) -> None:
        pg.init()
        pg.display.set_mode((width, height), pg.OPENGL|pg.DOUBLEBUF)
        glClearColor(0.1, 0.1, 0.1, 0.1)
        self.shader = self.create_shader("shaders/vertex.glsl", "shaders/fragment.glsl")
        glUseProgram(self.shader)
        glUniform1i(glGetUniformLocation(self.shader, "tex"), 0)
        glUniformMatrix4fv(glGetUniformLocation(self.shader, "projectionMatrix"), 1, GL_TRUE, self.get_projection_matrix(0.1, 100000, width/height, 90))
        glActiveTexture(GL_TEXTURE0)
        glEnable(GL_DEPTH_TEST)
        self.view_matrix = mat4.create_identity()
    
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

    def render_objects(self, objects: list[GameObject]):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glUniformMatrix4fv(glGetUniformLocation(self.shader, "viewMatrix"), 1, GL_FALSE, self.view_matrix)
        for obj in objects:
            if obj.render_component.active:
                glUniformMatrix4fv(glGetUniformLocation(self.shader, "modelMatrix"), 1, GL_FALSE, obj.render_component.model_matrix)
                obj.render_component.texture2d.use()
                glBindVertexArray(obj.render_component.vao)
                glDrawArrays(GL_TRIANGLES, 0, len(obj.render_component.vertices))

        pg.display.flip()

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