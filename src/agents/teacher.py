from typing import List, Optional, Tuple
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
        self.child_teleported = 0

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
                y_min <= child.position.y < y_max and
                not classroom.is_position_safe_zone(child.position.x, child.position.y))  # Add safe zone check
        ]

    def _get_area_center(self, classroom: 'Classroom') -> Position:
        x_min, x_max, y_min, y_max = self.zone
        return Position((x_min + x_max) // 2, (y_min + y_max) // 2)

    def choose_move(self, classroom: 'Classroom') -> Optional[Position]:
        # Only get children that are not in the safe zone
        children_in_area = self._find_children_in_area(classroom)
        
        # If no valid children are found outside safe zone, patrol area center
        if not children_in_area:
            target = self._get_area_center(classroom)
        else:
            # Find highest priority child that's not in safe zone
            target_child = None
            for strategy in self.STRATEGY_PRIORITY:
                for child in children_in_area:
                    if child.strategy == strategy:
                        target_child = child
                        break
                if target_child:
                    break
            
            # If no priority children found, target nearest child outside safe zone
            if not target_child and children_in_area:
                target_child = min(children_in_area, 
                                 key=lambda c: self.position.distance_to(c.position))
            
            target = target_child.position if target_child else self._get_area_center(classroom)
        
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
                classroom.grid[new_y][new_x] == CellType.EMPTY and
                not classroom.is_position_safe_zone(new_x, new_y)):  # Add safe zone check
                moves.append(Position(new_x, new_y))
        return moves