from typing import List, Optional, Tuple
import random
from .base_agent import Agent
from ..position import Position
from ..enums import AgentState, CellType, MovementStrategy

class Teacher(Agent):
    # Define the strategy priority list
    STRATEGY_PRIORITY = [
        MovementStrategy.AVOIDANCE,
        MovementStrategy.WALL_HUGGER,
        MovementStrategy.CANDY_HOARDER,
        MovementStrategy.STRATEGIC_TIMING,
        MovementStrategy.DIRECTIONAL_BIAS,
        MovementStrategy.GROUP_SEEKER,
        MovementStrategy.SAFE_EXPLORER,
        MovementStrategy.CANDY_SEEKER,
        MovementStrategy.RANDOM_WALK,
        MovementStrategy.UNPREDICTABLE
    ]

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
        
        # Check for any children using strategies from the priority list
        for strategy in self.STRATEGY_PRIORITY:
            for child in children_in_area:
                if child.strategy == strategy:
                    target = child.position
                    break
            else:
                continue  # No child found for this strategy, continue to the next
            break  # Found a child, break out of the outer loop
        else:
            # No children found matching priority strategies
            # Fall back to targeting the nearest child, if any
            if children_in_area:
                target = min(children_in_area, 
                             key=lambda c: self.position.distance_to(c.position)).position
            else:
                # If no children around at all, move towards the area center
                target = self._get_area_center(classroom)
        
        possible_moves = self._get_valid_moves(classroom)
        if not possible_moves:
            return None
            
        # Move towards the chosen target position
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