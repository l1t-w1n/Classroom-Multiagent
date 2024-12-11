
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

class MovementStrategy(Enum):
    """Different movement strategies that child agents can employ"""
    RANDOM_WALK = 0      # Original: Moves randomly
    CANDY_SEEKER = 1     # Original: Moves toward nearest candy
    AVOIDANCE = 2        # Original: Stays away from teacher
    DIRECTIONAL_BIAS = 3 # Original: Prefers specific directions
    STRATEGIC_TIMING = 4 # Original: Moves at specific intervals
    
    # New strategies
    WALL_HUGGER = 5      # Stays close to classroom walls for safety
    GROUP_SEEKER = 6     # Tries to stay close to other children
    CANDY_HOARDER = 7    # Focuses on areas with multiple candies
    SAFE_EXPLORER = 8    # Alternates between safe zone and exploration
    UNPREDICTABLE = 9    # Randomly switches between different strategies