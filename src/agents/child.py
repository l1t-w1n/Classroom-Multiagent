import random
import time
from typing import List, Optional

from .base_agent import Agent
from ..position import Position
from ..enums import AgentState, MovementStrategy, CellType

class Child(Agent):
    """Represents a child agent in the simulation"""
    def __init__(self, position: Position, strategy: MovementStrategy):
        super().__init__(position)
        self.strategy = strategy
        self.state = AgentState.FREE
        self.last_move_time = time.time()
        self.move_cooldown = random.uniform(0.5, 2.0)
        self.preferred_direction = random.choice([(0, 1), (1, 0), (0, -1), (-1, 0)])

    def choose_move(self, classroom: 'Classroom') -> Optional[Position]:
        """Determines the next move based on the child's strategy"""
        if self.state == AgentState.CAPTURED:
            return None

        current_time = time.time()
        if self.strategy == MovementStrategy.STRATEGIC_TIMING:
            if current_time - self.last_move_time < self.move_cooldown:
                return None

        possible_moves = self._get_valid_moves(classroom)
        if not possible_moves:
            return None

        self.last_move_time = current_time

        if self.strategy == MovementStrategy.CANDY_SEEKER:
            return self._find_nearest_candy_move(classroom, possible_moves)
        elif self.strategy == MovementStrategy.AVOIDANCE:
            return self._find_safest_move(classroom, possible_moves)
        elif self.strategy == MovementStrategy.DIRECTIONAL_BIAS:
            return self._find_directional_move(possible_moves)
        else:  # RANDOM_WALK
            return random.choice(possible_moves)

    def _get_valid_moves(self, classroom: 'Classroom') -> List[Position]:
        """Returns list of valid positions the child can move to"""
        moves = []
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            new_x = self.position.x + dx
            new_y = self.position.y + dy
            if (0 <= new_x < classroom.width and 
                0 <= new_y < classroom.height and 
                classroom.grid[new_y][new_x] == CellType.EMPTY):
                moves.append(Position(new_x, new_y))
        return moves

    def _find_nearest_candy_move(self, classroom: 'Classroom', possible_moves: List[Position]) -> Position:
        """Finds move that brings child closest to nearest candy"""
        nearest_candy = None
        min_distance = float('inf')
        
        for y in range(classroom.height):
            for x in range(classroom.width):
                if classroom.grid[y][x] == CellType.CANDY:
                    candy_pos = Position(x, y)
                    dist = self.position.distance_to(candy_pos)
                    if dist < min_distance:
                        min_distance = dist
                        nearest_candy = candy_pos

        if nearest_candy:
            return min(possible_moves, 
                      key=lambda pos: pos.distance_to(nearest_candy))
        return random.choice(possible_moves)

    def _find_safest_move(self, classroom: 'Classroom', possible_moves: List[Position]) -> Position:
        """Finds move that maximizes distance from teacher"""
        if not possible_moves:
            return None
            
        teacher_pos = classroom.teacher.position if classroom.teacher else None
        if not teacher_pos:
            return random.choice(possible_moves)
            
        return max(possible_moves,
                  key=lambda pos: pos.distance_to(teacher_pos))

    def _find_directional_move(self, possible_moves: List[Position]) -> Position:
        """Chooses move based on preferred direction"""
        preferred_x = self.position.x + self.preferred_direction[0]
        preferred_y = self.position.y + self.preferred_direction[1]
        preferred_pos = Position(preferred_x, preferred_y)
        
        for move in possible_moves:
            if move.x == preferred_x and move.y == preferred_y:
                return move
                
        return random.choice(possible_moves)