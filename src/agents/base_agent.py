from ..position import Position

class Agent:
    """Base class for all agents in the simulation"""
    def __init__(self, position: Position):
        self.position = position
        self.previous_position = position  # Stores the last position for movement tracking

    def move(self, new_position: Position):
        """Updates agent position while keeping track of previous position"""
        self.previous_position = Position(self.position.x, self.position.y)
        self.position = new_position