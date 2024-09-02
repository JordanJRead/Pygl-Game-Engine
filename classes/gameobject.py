from classes.transform import Transform
from classes.rendercomponent import RenderComponent
import classes.rendercomponent as rendercomponent
from typing import Self
from classes.monobehaviour import MonoBehaviour

class GameObject:
    def __init__(self, transform: Transform, parent: Self | None = None, render_component: RenderComponent | None = None, scripts: list[MonoBehaviour] = []) -> None:
        self.transform = transform
        self.parent = parent
        self.render_component = render_component
        self.scripts = scripts
        for script in self.scripts:
            script.game_object = self
            script.start()

        if self.render_component:
            self.render_component.model_matrix = rendercomponent.create_entire_model_matrix(self.transform, self.parent)
    
    def destroy(self):
        if self.render_component:
            self.render_component.destroy()
    
    def update_transform(self, transform: Transform):
        self.transform = transform
        if self.render_component:
            self.render_component.model_matrix = rendercomponent.create_entire_model_matrix(self.transform, self.parent)