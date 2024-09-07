from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from gameobject import GameObject
    
class MonoBehaviour:
    def __init__(self) -> None:
        self.game_object: GameObject | None = None
        self.delta_time = 0
        self.app = None
    def start(self):
        pass
    def update(self):
        pass
    def end(self):
        pass