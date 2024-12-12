from typing import List, Optional, Tuple
import random
from .base_agent import Agent
from ..position import Position
from ..enums import AgentState, CellType

class Teacher(Agent):
    def __init__(self, position: Position, zone: Tuple[int, int, int, int]):
        super().__init__(position)
        self.zone = zone

    def is_adjacent_to(self, other_pos: Position) -> bool:
        dx = abs(self.position.x - other_pos.x)
        dy = abs(self.position.y - other_pos.y)
        return dx <= 1 and dy <= 1 and not (dx == 0 and dy == 0)

    def _find_children_in_area(self, classroom: 'Classroom') -> List['Child']:
        x_min, x_max, y_min, y_max = self.zone
        
        return [
            child for child in classroom.children
            if (child.can_move() and 
                x_min <= child.position.x < x_max and
                y_min <= child.position.y < y_max)
        ]

    def _get_area_center(self, classroom: 'Classroom') -> Position:
        x_min, x_max, y_min, y_max = self.zone
        return Position((x_min + x_max) // 2, (y_min + y_max) // 2)

    def choose_move(self, classroom: 'Classroom') -> Optional[Position]:
        children_in_area = self._find_children_in_area(classroom)
        
        if not children_in_area and random.random() < 0.1:
            children_in_area = [
                child for child in classroom.children
                if child.can_move()
            ]
        
        if children_in_area:
            nearest_child = min(children_in_area, 
                              key=lambda c: self.position.distance_to(c.position))
            target = nearest_child.position
        else:
            target = self._get_area_center(classroom)
        
        possible_moves = self._get_valid_moves(classroom)
        if not possible_moves:
            return None
            
        return min(possible_moves,
                  key=lambda pos: pos.distance_to(target))

    def _get_valid_moves(self, classroom: 'Classroom') -> List[Position]:
        moves = []
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            new_x = self.position.x + dx
            new_y = self.position.y + dy
            if (0 <= new_x < classroom.width and 
                0 <= new_y < classroom.height and 
                classroom.grid[new_y][new_x] == CellType.EMPTY):
                moves.append(Position(new_x, new_y))
        return moves