from typing import List, Optional
from .base_agent import Agent
from ..position import Position
from ..enums import AgentState, CellType, MovementStrategy

class Teacher(Agent):
    """Represents the teacher agent in the simulation"""
    def __init__(self, position: Position):
        super().__init__(position)
        # Define strategy priority (highest to lowest)
        self.strategy_priority = [
            MovementStrategy.AVOIDANCE,      # Catch avoiders first
            MovementStrategy.DIRECTIONAL_BIAS,# Then predictable movers
            MovementStrategy.CANDY_SEEKER,    # Then candy seekers
            MovementStrategy.WALL_HUGGER,     # Then wall huggers
            MovementStrategy.GROUP_SEEKER,    # Then group seekers
            MovementStrategy.CANDY_HOARDER,   # Then hoarders
            MovementStrategy.SAFE_EXPLORER,   # Then explorers
            MovementStrategy.STRATEGIC_TIMING,# Then strategic timers
            MovementStrategy.RANDOM_WALK,     # Then random walkers
            MovementStrategy.UNPREDICTABLE    # Finally unpredictable ones
        ]
    def is_adjacent_to(self, other_pos: Position) -> bool:
        """
        Determines if another position is adjacent to the teacher, including diagonal positions.
        
        This method checks all eight surrounding cells:
        - The four cardinal directions (up, down, left, right)
        - The four diagonal positions (corners)
        
        For example, if the teacher is at position (x,y), it will check:
        (x-1, y-1)  (x, y-1)  (x+1, y-1)
        (x-1, y)     (x,y)    (x+1, y)
        (x-1, y+1)  (x, y+1)  (x+1, y+1)
        
        Args:
            other_pos: The position to check for adjacency
            
        Returns:
            bool: True if the position is in any of the eight surrounding cells
        """
        # Calculate the absolute differences in x and y coordinates
        dx = abs(self.position.x - other_pos.x)
        dy = abs(self.position.y - other_pos.y)
        
        # A position is adjacent (including diagonals) if both differences are at most 1
        # This means we're either:
        # - In a cardinal direction (one difference is 1, the other is 0)
        # - In a diagonal position (both differences are 1)
        # - In the same position (both differences are 0)
        return dx <= 1 and dy <= 1 and not (dx == 0 and dy == 0)

    def choose_move(self, classroom: 'Classroom') -> Optional[Position]:
        """
        Determines the teacher's next move. The teacher will:
        1. Find the nearest child outside the safe zone
        2. Move toward that child
        3. Teleport the child to the safe zone if adjacent
        """
        return self._find_nearest_child_move(classroom)

    def _find_nearest_child_move(self, classroom: 'Classroom') -> Optional[Position]:
        target_child = None
        min_distance = float('inf')
        
        # Check each strategy in priority order
        for priority_strategy in self.strategy_priority:
            nearest_for_strategy = None
            min_distance_for_strategy = float('inf')
            
            # Look for children with current strategy
            for child in classroom.children:
                if (child.state == AgentState.FREE and 
                    child.strategy == priority_strategy and 
                    child.can_move() and 
                    not any(safe_pos.x == child.position.x and 
                           safe_pos.y == child.position.y 
                           for safe_pos in classroom.safe_zone)):
                    
                    distance = self.position.distance_to(child.position)
                    if distance < min_distance_for_strategy:
                        min_distance_for_strategy = distance
                        nearest_for_strategy = child
            
            # If we found a child with this strategy, they become our target
            if nearest_for_strategy:
                target_child = nearest_for_strategy
                break
        
        if not target_child:
            return None
            
        # Handle movement toward target child as before...
        if self.is_adjacent_to(target_child.position):
            return None
            
        possible_moves = self._get_valid_moves(classroom)
        if not possible_moves:
            return None
            
        return min(possible_moves,
                  key=lambda pos: pos.distance_to(target_child.position))

    def _get_valid_moves(self, classroom: 'Classroom') -> List[Position]:
        """Returns list of valid positions the teacher can move to"""
        moves = []
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            new_x = self.position.x + dx
            new_y = self.position.y + dy
            if (0 <= new_x < classroom.width and 
                0 <= new_y < classroom.height and 
                classroom.grid[new_y][new_x] == CellType.EMPTY):
                moves.append(Position(new_x, new_y))
        return moves
