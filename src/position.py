import numpy as np

class Position:
    """Represents a position in the classroom grid"""
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
    
    def distance_to(self, other: 'Position') -> float:
        """Calculates Euclidean distance to another position"""
        return np.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)
    
    def __eq__(self, other):
        """Enables position comparison with == operator"""
        if not isinstance(other, Position):
            return False
        return self.x == other.x and self.y == other.y