from typing import List, Optional
from .base_agent import Agent
from ..position import Position
from ..enums import AgentState, CellType

class Teacher(Agent):
    """Represents the teacher agent in the simulation"""
    def __init__(self, position: Position):
        super().__init__(position)
        self.escorting_child: Optional['Child'] = None

    def choose_move(self, classroom: 'Classroom') -> Optional[Position]:
        """Determines teacher's next move based on current situation"""
        # If already escorting a child, focus on getting them to the safe zone
        if self.escorting_child:
            return self._escort_to_safe_zone(classroom)
            
        # Only look for new children if not currently escorting anyone
        return self._find_nearest_child_move(classroom)

    def _find_nearest_child_move(self, classroom: 'Classroom') -> Optional[Position]:
        """Finds best move to catch nearest free child"""
        # Don't look for new children if already escorting one
        if self.escorting_child:
            return None
            
        nearest_child = None
        min_distance = float('inf')
        
        # Find the nearest free child
        for child in classroom.children:
            if child.state == AgentState.FREE:
                distance = self.position.distance_to(child.position)
                if distance < min_distance:
                    min_distance = distance
                    nearest_child = child
        
        if not nearest_child:
            return None
            
        # Only capture if we're in the same cell
        if self.position == nearest_child.position:
            nearest_child.state = AgentState.CAPTURED
            self.escorting_child = nearest_child
            return None
            
        # Otherwise, move toward the child
        possible_moves = self._get_valid_moves(classroom)
        if not possible_moves:
            return None
            
        return min(possible_moves,
                  key=lambda pos: pos.distance_to(nearest_child.position))

    def _escort_to_safe_zone(self, classroom: 'Classroom') -> Optional[Position]:
        """Returns move to escort captured child back to safe zone"""
        if not self.escorting_child:
            return None
            
        # Find nearest safe zone position
        nearest_safe = min(classroom.safe_zone,
                          key=lambda pos: self.position.distance_to(pos))
        
        # If we're at safe zone, release child
        if self.position.distance_to(nearest_safe) == 0:  # Changed from <= 1 to == 0
            self.escorting_child.state = AgentState.FREE
            self.escorting_child = None
            return None
            
        # Move toward safe zone
        possible_moves = self._get_valid_moves(classroom)
        if not possible_moves:
            return None
            
        # Choose the move that gets us closest to the safe zone
        return min(possible_moves,
                  key=lambda pos: pos.distance_to(nearest_safe))

    def _get_valid_moves(self, classroom: 'Classroom') -> List[Position]:
        """Returns list of valid positions the teacher can move to"""
        moves = []
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            new_x = self.position.x + dx
            new_y = self.position.y + dy
            if (0 <= new_x < classroom.width and 
                0 <= new_y < classroom.height and 
                classroom.grid[new_y][new_x] == CellType.EMPTY):  # Only allow moving to empty cells
                moves.append(Position(new_x, new_y))
        return moves