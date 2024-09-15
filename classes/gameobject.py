from __future__ import annotations
from classes.transform import Transform
from classes.rendercomponent import RenderComponent
import classes.rendercomponent as rendercomponent
from classes.monobehaviour import MonoBehaviour
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from main import App

# Scripts is a list of (classtype, arguments)
class GameObject:
    def __init__(self, app: App, name: str, local_transform: Transform = Transform.zero(), children: list[GameObject] = [], render_component: RenderComponent = None, scripts: list[tuple[any, list[any]]] = []) -> None:
        self.parent = None
        self.app = app
        self.children = children
        self.name = name
        self.local_transform = local_transform
        self.render_component = render_component
        if self.render_component == None:
            self.render_component = RenderComponent("", "", False)

        self.scripts = scripts # For converting to json
        self.components: list[MonoBehaviour] = []

        for script in scripts:
            self.components.append(script[0](self, self.app, *script[1]))
        for child in self.children:
            child.parent = self
            
    
    def destroy(self):
        if self.render_component:
            self.render_component.destroy()
        for custom_object in self.components:
            custom_object.end()
    
    def update_transform(self, transform: Transform):
        self.local_transform = transform
        if self.render_component:
            self.render_component.model_matrix = rendercomponent.create_entire_model_matrix(self.local_transform, self.parent)
        
    def get_component(self, wanted_type):
        for component in self.components:
            if type(component) == wanted_type:
                return component