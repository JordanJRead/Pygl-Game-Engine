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
        for script in self.scripts:
            script.end()
    
    def update_transform(self, transform: Transform):
        self.transform = transform
        if self.render_component:
            self.render_component.model_matrix = rendercomponent.create_entire_model_matrix(self.transform, self.parent)