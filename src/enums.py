
from enum import Enum

class CellType(Enum):
    """Represents the different types of cells that can exist in the classroom grid"""
    EMPTY = 0      # An empty cell that agents can move into
    SAFE_ZONE = 1  # Part of the designated safe area, typically near teacher's desk
    CANDY = 2      # A candy that children can collect
    CHILD = 3      # A cell occupied by a child agent
    TEACHER = 4    # A cell occupied by the teacher agent

class AgentState(Enum):
    """Represents the possible states a child agent can be in"""
    FREE = 0       # Child is free to move and collect candy
    CAPTURED = 1   # Child has been caught by teacher and is being escorted

class MovementStrategy(Enum):
    """Different movement strategies that child agents can employ"""
    STRATEGIC_TIMING = 0  # Moves at specific time intervals
    AVOIDANCE = 1        # Tries to stay away from the teacher
    DIRECTIONAL_BIAS = 2  # Prefers moving in certain directions
    RANDOM_WALK = 3      # Moves randomly
    CANDY_SEEKER = 4     # Actively seeks out candy