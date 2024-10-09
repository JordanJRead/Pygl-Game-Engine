from __future__ import annotations
from classes.transform import Transform
from classes.rendercomponent import RenderComponent
import classes.transform as transform
from classes.monobehaviour import MonoBehaviour
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from main import App

# Scripts is a list of (classtype, arguments)
class GameObject:
    def __init__(self, app: App, name: str, local_transform: Transform = Transform.identity(), children: list[GameObject] = None, render_component: RenderComponent = None, scripts: list[tuple[type, list[any]]] = None) -> None:
        if children is None:
            children = []
        if scripts is None:
            scripts = []
        self.parent: GameObject | None = None
        self.app = app
        self.children = children
        self.name = name
        self.local_transform = local_transform
        self.render_component = render_component
        if self.render_component == None:
            self.render_component = RenderComponent("", "", False)

        self.scripts = scripts # For converting to json, [(classname, [arg1, arg2, arg3])]
        self.components: list[MonoBehaviour] = []

        for script in scripts:
            self.components.append(script[0](self, self.app, *script[1]))
        for child in self.children:
            child.parent = self
            
    def update_script_args(self, cls: type, args: list[any]):
        for component in self.components:
            if type(component) == cls:
                component.end()
        for i, script in enumerate(self.scripts):
            if script[0] == cls:
                self.scripts[i] = [script[0], args]

    def destroy(self):
        if self.parent:
            self.parent.children.remove(self)
        if self.render_component:
            self.render_component.destroy()
        for custom_object in self.components:
            custom_object.end()
        for child in self.children:
            child.destroy()
        if self in self.app.game_objects:
            self.app.game_objects.remove(self)
    
    def update_transform(self, new_transform: Transform):
        self.local_transform = new_transform
        if self.render_component:
            self.local_transform.model_matrix = transform.create_entire_model_matrix(self.local_transform, self.parent)
        for child in self.children:
            child.update_transform(child.local_transform)
        
    def get_component(self, wanted_type):
        for component in self.components:
            if type(component) == wanted_type:
                return component
    
    def add_child(self, child: GameObject, index: int | None = None):
        if child.parent:
            child.parent.children.remove(child)
        if index == None:
            self.children.append(child)
        else:
            self.children.insert(index, child)
        child.parent = self