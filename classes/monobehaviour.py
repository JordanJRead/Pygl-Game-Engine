from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from gameobject import GameObject
    from main import App
    
class MonoBehaviour:
    def __init__(self, game_object: GameObject, app: App) -> None:
        self.game_object = game_object
        self.app = app
        self.delta_time = 0
    def start(self):
        pass
    def update(self):
        pass
    def end(self):
        pass