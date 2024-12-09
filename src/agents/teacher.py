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
        if self.escorting_child:
            return self._escort_to_safe_zone(classroom)
        return self._find_nearest_child_move(classroom)

    def _find_nearest_child_move(self, classroom: 'Classroom') -> Optional[Position]:
        """Finds best move to catch nearest free child"""
        nearest_child = None
        min_distance = float('inf')
        
        for child in classroom.children:
            if child.state == AgentState.FREE:
                distance = self.position.distance_to(child.position)
                if distance < min_distance:
                    min_distance = distance
                    nearest_child = child
        
        if not nearest_child:
            return None
            
        if min_distance <= 1:
            return Position(nearest_child.position.x, nearest_child.position.y)
            
        possible_moves = self._get_valid_moves(classroom)
        if not possible_moves:
            return None
            
        return min(possible_moves,
                  key=lambda pos: pos.distance_to(nearest_child.position))

    def _escort_to_safe_zone(self, classroom: 'Classroom') -> Optional[Position]:
        """Returns move to escort captured child back to safe zone"""
        if not self.escorting_child:
            return None
            
        nearest_safe = min(classroom.safe_zone,
                          key=lambda pos: self.position.distance_to(pos))
        
        if self.position.distance_to(nearest_safe) <= 1:
            self.escorting_child.state = AgentState.FREE
            self.escorting_child = None
            return None
            
        possible_moves = self._get_valid_moves(classroom)
        if not possible_moves:
            return None
            
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
                classroom.grid[new_y][new_x] in [CellType.EMPTY, CellType.CHILD]):
                moves.append(Position(new_x, new_y))
        return moves