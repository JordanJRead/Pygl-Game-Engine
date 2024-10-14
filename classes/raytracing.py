from classes.rendercomponent import RenderComponent
from classes.vec3 import Vec3
from classes.gameobject import GameObject
import numpy as np

def ray_triangle_intersection(origin: Vec3, dir: Vec3, triangle_points: list[Vec3]) -> float | None:
    """Finds the t value of the intersection between a ray and a triangle"""
    epsilon = 1e-6

    edge_1 = triangle_points[1] - triangle_points[0]
    edge_2 = triangle_points[2] - triangle_points[0]
    ray_cross_e2 = dir.cross(edge_2)
    det = edge_1 * ray_cross_e2

    if det > -epsilon and det < epsilon:
        return None
    
    inv_det = 1 / det
    s = origin - triangle_points[0]
    u = inv_det * (s * ray_cross_e2)

    if u < 0 or u > 1:
        return None
    
    s_cross_e1 = s.cross(edge_1)
    v = inv_det * (dir * s_cross_e1)

    if v < 0 or u + v > 1:
        return None
    
    t = inv_det * (edge_2 * s_cross_e1)

    if t > epsilon:
        # return origin + dir * t
        return t
    return None

def find_t_of_game_object(origin: Vec3, dir: Vec3, game_object: GameObject, view_matrix, default_render_component: RenderComponent | None = None) -> float:
    """Returns the t value of the intersection, if it exists, between a ray in camera space and a game object"""
    smallest_t = None
    render_component = game_object.render_component
    if not render_component.is_active and default_render_component:
        render_component = default_render_component
    if render_component.is_active:
        triangle_count = len(render_component.vertices) // 3 // render_component.vertice_data_size
        triangle_data_size = 3 * render_component.vertice_data_size
        for triangle_start_index in range(0, triangle_data_size * (triangle_count - 1) + 1, 8):
            model_triangle_points: list[Vec3] = [
                Vec3(render_component.vertices[triangle_start_index], render_component.vertices[triangle_start_index + 1], render_component.vertices[triangle_start_index + 2]),
                Vec3(render_component.vertices[triangle_start_index + render_component.vertice_data_size], render_component.vertices[triangle_start_index + render_component.vertice_data_size + 1], render_component.vertices[triangle_start_index + render_component.vertice_data_size + 2]),
                Vec3(render_component.vertices[triangle_start_index + render_component.vertice_data_size * 2], render_component.vertices[triangle_start_index + render_component.vertice_data_size * 2 + 1], render_component.vertices[triangle_start_index + render_component.vertice_data_size * 2 + 2])
            ]
            world_triangle_points: list[Vec3] = [
                model_triangle_points[0].mat_mul(game_object.local_transform.model_matrix, True),
                model_triangle_points[1].mat_mul(game_object.local_transform.model_matrix, True),
                model_triangle_points[2].mat_mul(game_object.local_transform.model_matrix, True)
            ]
            view_triangle_points: list[Vec3] = [
                world_triangle_points[0].mat_mul(view_matrix, True),
                world_triangle_points[1].mat_mul(view_matrix, True),
                world_triangle_points[2].mat_mul(view_matrix, True)
            ]
            t_value = ray_triangle_intersection(origin, dir, view_triangle_points)
            if t_value and smallest_t:
                if t_value < smallest_t:
                    smallest_t = t_value
            elif not smallest_t and t_value:
                smallest_t = t_value
    return smallest_t

# FIXME children?
def ray_cast_game_objects(origin: Vec3, dir: Vec3, game_objects: list[GameObject], view_matrix, default_render_component: RenderComponent | None = None) -> GameObject | None:
    """Given a ray in camera space, returns the hit game object if it exists"""
    smallest_t = None
    closest_object = None
    for game_object in game_objects:
        t_value = find_t_of_game_object(origin, dir, game_object, view_matrix, default_render_component)
        if t_value and smallest_t:
            if t_value < smallest_t:
                smallest_t = t_value
                closest_object = game_object
        elif not smallest_t and t_value:
            smallest_t = t_value
            closest_object = game_object
    return closest_object