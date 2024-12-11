from typing import List, Optional
from .base_agent import Agent
from ..position import Position
from ..enums import AgentState, CellType

class Teacher(Agent):
    """Represents the teacher agent in the simulation"""
    def __init__(self, position: Position):
        super().__init__(position)
        # Removed escorting_child since we're not using it anymore

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
        """
        Finds and moves toward the nearest eligible child. When adjacent,
        immediately teleports the child to the safe zone.
        """
        nearest_child = None
        min_distance = float('inf')
        
        # Find the nearest eligible child (free and outside safe zone)
        for child in classroom.children:
            # Check if child is outside safe zone
            is_in_safe_zone = any(
                safe_pos.x == child.position.x and safe_pos.y == child.position.y
                for safe_pos in classroom.safe_zone
            )
            
            # Only consider free children outside the safe zone that can move
            if child.state == AgentState.FREE and not is_in_safe_zone and child.can_move():
                distance = self.position.distance_to(child.position)
                if distance < min_distance:
                    min_distance = distance
                    nearest_child = child
        
        if not nearest_child:
            return None
            
        # If adjacent to a child, teleport them to the safe zone
        if self.is_adjacent_to(nearest_child.position):
            # Find the nearest safe zone position
            nearest_safe = min(classroom.safe_zone,
                             key=lambda pos: nearest_child.position.distance_to(pos))
            
            # Update grid and teleport child
            classroom.grid[nearest_child.position.y][nearest_child.position.x] = CellType.EMPTY
            classroom.grid[nearest_safe.y][nearest_safe.x] = CellType.CHILD
            nearest_child.position = nearest_safe
            
            # Apply cooldown to the child
            nearest_child.set_cooldown(5.0)  # 5 second cooldown
            return None
            
        # Move toward the child if not adjacent
        possible_moves = self._get_valid_moves(classroom)
        if not possible_moves:
            return None
            
        # Choose the move that gets us closest to the target child
        return min(possible_moves,
                  key=lambda pos: pos.distance_to(nearest_child.position))

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
