from classes.transform import Transform
from classes.rendercomponent import RenderComponent
import classes.rendercomponent as rendercomponent
from classes.monobehaviour import MonoBehaviour

class GameObject:
    def __init__(self, name: str, transform: Transform, parent_name: str, render_component: RenderComponent, scripts: list[MonoBehaviour]) -> None:
        self.name = name
        self.transform = transform
        self.parent_name = parent_name
        self.parent = None
        self.render_component = render_component
        self.scripts = scripts
        for script in self.scripts:
            script.game_object = self

    def init_parent(self, game_objects):
        for game_object in game_objects:
            if game_object.name == self.parent_name:
                self.parent = game_object
        if self.render_component:
            self.render_component.model_matrix = rendercomponent.create_entire_model_matrix(self.transform, self.parent)
    
    def destroy(self):
        if self.render_component:
            self.render_component.destroy()
    
    def update_transform(self, transform: Transform):
        self.transform = transform
        if self.render_component:
            self.render_component.model_matrix = rendercomponent.create_entire_model_matrix(self.transform, self.parent)

# def load_from_file(file_path) -> list[GameObject]:
#     with open(file_path) as file:
#         file = [l.strip('\n\r') for l in file]
#         for line in file:
#             if line[0] != "#":
#                 name, index = get_coded_info(0, line)
#                 pos_x, index = get_coded_info(index, line, float)
#                 pos_y, index = get_coded_info(index, line, float)
#                 pos_z, index = get_coded_info(index, line, float)
#                 scale_x, index = get_coded_info(index, line, float)
#                 scale_y, index = get_coded_info(index, line, float)
#                 scale_z, index = get_coded_info(index, line, float)
#                 rot_x, index = get_coded_info(index, line, float)
#                 rot_y, index = get_coded_info(index, line, float)
#                 rot_z, index = get_coded_info(index, line, float)
#                 has_parent, index = get_coded_info(index, line, bool)
#                 parent_name, index = get_coded_info(index, line, str)
#                 has_renderer, index = get_coded_info(index, line, bool)
#                 object_path, index = get_coded_info(index, line, str)
#                 image_path, index = get_coded_info(index, line, str)
#                 script_count, index = get_coded_info(index, line, int)
#                 script_names = []
#                 args = []
#                 # FIXME script name
#                 for i in range(script_count):
#                     script_name, index = get_coded_info(index, line, int)
#                     script_names.append(script_name)
#                     arg_count, index = get_coded_info(index, line, int)
#                     for j in arg_count:
#                         arg_type, index = get_coded_info(index, line, str)
#                         match arg_type:
#                             case "str":
#                                 arg_type = str
#                             case "float":
#                                 arg_type = float
#                             case "int":
#                                 arg_type = int
#                             case "bool":
#                                 arg_type = bool
#                         arg_value, index = get_coded_info(index, line, arg_type)
#                         args.append(arg_value)
#         creation_line = f"GameObject('{name}', Transform(Vec3({pos_x}, {pos_y}, {pos_z}), Vec3({scale_x}, {scale_y}, {scale_z}), Vec3({rot_x}, {rot_y}, {rot_z}))"
#         if has_parent:
#             creation_line += f", {parent_name}"
#         if has_renderer:
#             creation_line += f", RenderComponent('{object_path}', '{image_path}')"
#         if script_count > 0:
#             creation_line += ", ["
#             for script in script_names:
#                 creation_line += f"{script}("
#                 for arg in ar
#                 creation_line += ")"

#         creation_line += "]"

#         creation_line += ")"


# def get_coded_info(index: int, line: str, val_type = str):
#     close_brace_index = line.index("}", index)
#     length = line[index+1 : close_brace_index]
#     length = int(length)
#     return val_type(line[close_brace_index+1 : close_brace_index+length], close_brace_index+length+1)

