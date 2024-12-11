from typing import List, Optional
import random
import time
from .base_agent import Agent
from ..position import Position
from ..enums import AgentState, MovementStrategy, CellType

class Child(Agent):
    """
    Represents a child agent in the simulation that moves around the classroom
    collecting candies while avoiding the teacher. Each child has a specific
    movement strategy and can be temporarily immobilized by cooldown.
    """
    def __init__(self, position: Position, strategy: MovementStrategy):
        super().__init__(position)
        self.strategy = strategy
        self.state = AgentState.FREE
        self.cooldown_until = 0
        self.last_move_time = time.time()
        self.move_cooldown = random.uniform(0.5, 2.0)
        self.preferred_direction = random.choice([(0, 1), (1, 0), (0, -1), (-1, 0)])
        # For unpredictable strategy
        self.current_substrategy = MovementStrategy.RANDOM_WALK
        self.strategy_switch_time = time.time() + random.uniform(5.0, 10.0)

    def choose_move(self, classroom: 'Classroom') -> Optional[Position]:
        if not self.can_move():
            return None

        current_time = time.time()
        if self.strategy == MovementStrategy.STRATEGIC_TIMING:
            if current_time - self.last_move_time < self.move_cooldown:
                return None

        possible_moves = self._get_valid_moves(classroom)
        if not possible_moves:
            return None

        self.last_move_time = current_time

        # Handle strategy selection
        if self.strategy == MovementStrategy.UNPREDICTABLE:
            if current_time >= self.strategy_switch_time:
                self.current_substrategy = random.choice([
                    strat for strat in MovementStrategy 
                    if strat != MovementStrategy.UNPREDICTABLE
                ])
                self.strategy_switch_time = current_time + random.uniform(5.0, 10.0)
            return self._execute_strategy(self.current_substrategy, classroom, possible_moves)

        return self._execute_strategy(self.strategy, classroom, possible_moves)

    def _execute_strategy(self, strategy: MovementStrategy, classroom: 'Classroom', 
                         possible_moves: List[Position]) -> Optional[Position]:
        """Execute the specified movement strategy"""
        strategy_map = {
            MovementStrategy.RANDOM_WALK: lambda: random.choice(possible_moves),
            MovementStrategy.CANDY_SEEKER: lambda: self._find_nearest_candy_move(classroom, possible_moves),
            MovementStrategy.AVOIDANCE: lambda: self._find_safest_move(classroom, possible_moves),
            MovementStrategy.DIRECTIONAL_BIAS: lambda: self._find_directional_move(possible_moves),
            MovementStrategy.WALL_HUGGER: lambda: self._find_wall_hugging_move(classroom, possible_moves),
            MovementStrategy.GROUP_SEEKER: lambda: self._find_group_move(classroom, possible_moves),
            MovementStrategy.CANDY_HOARDER: lambda: self._find_candy_rich_area_move(classroom, possible_moves),
            MovementStrategy.SAFE_EXPLORER: lambda: self._find_safe_exploration_move(classroom, possible_moves)
        }
        return strategy_map.get(strategy, lambda: random.choice(possible_moves))()

    def _find_wall_hugging_move(self, classroom: 'Classroom', possible_moves: List[Position]) -> Position:
        """Prefers moves that keep the child close to classroom walls"""
        def wall_score(pos: Position) -> float:
            # High score for positions next to walls
            wall_proximity = min(
                pos.x, pos.y,
                classroom.width - 1 - pos.x,
                classroom.height - 1 - pos.y
            )
            return -wall_proximity  # Negative because we want to minimize distance to walls

        return max(possible_moves, key=wall_score)

    def _find_group_move(self, classroom: 'Classroom', possible_moves: List[Position]) -> Position:
        """Moves toward the largest group of other children"""
        def count_nearby_children(pos: Position, radius: int = 3) -> int:
            count = 0
            for child in classroom.children:
                if child != self and child.state == AgentState.FREE:
                    if pos.distance_to(child.position) <= radius:
                        count += 1
            return count

        return max(possible_moves, key=count_nearby_children)

    def _find_candy_rich_area_move(self, classroom: 'Classroom', possible_moves: List[Position]) -> Position:
        """Moves toward areas with multiple candies"""
        def candy_density_score(pos: Position, radius: int = 3) -> int:
            count = 0
            for y in range(max(0, pos.y - radius), min(classroom.height, pos.y + radius + 1)):
                for x in range(max(0, pos.x - radius), min(classroom.width, pos.x + radius + 1)):
                    if classroom.grid[y][x] == CellType.CANDY:
                        count += 1
            return count

        return max(possible_moves, key=candy_density_score)

    def _find_safe_exploration_move(self, classroom: 'Classroom', possible_moves: List[Position]) -> Position:
        """Alternates between staying near safe zone and exploring"""
        time_since_cooldown = time.time() - self.cooldown_until
        exploration_phase = (time_since_cooldown % 20) > 10  # Switch every 10 seconds
        
        if exploration_phase:
            # During exploration, behave like a candy seeker
            return self._find_nearest_candy_move(classroom, possible_moves)
        else:
            # During safe phase, stay closer to safe zone
            nearest_safe = min(classroom.safe_zone,
                             key=lambda pos: self.position.distance_to(pos))
            return min(possible_moves,
                      key=lambda pos: pos.distance_to(nearest_safe))

    def set_cooldown(self, duration: float):
        """
        Sets a cooldown period during which the child cannot move.
        
        Args:
            duration: The number of seconds the cooldown should last
        """
        self.cooldown_until = time.time() + duration

    def can_move(self) -> bool:
        """
        Checks if the child is allowed to move (not in cooldown).
        
        Returns:
            bool: True if the child can move, False if still in cooldown
        """
        return time.time() >= self.cooldown_until

    def choose_move(self, classroom: 'Classroom') -> Optional[Position]:
        """
        Determines the next move for the child based on their strategy.
        Takes into account cooldown and movement restrictions.
        
        Args:
            classroom: The current state of the classroom environment
            
        Returns:
            Optional[Position]: The position to move to, or None if no move is possible
        """
        # Check if movement is allowed
        if not self.can_move():
            return None

        # Handle strategic timing movement delays
        current_time = time.time()
        if self.strategy == MovementStrategy.STRATEGIC_TIMING:
            if current_time - self.last_move_time < self.move_cooldown:
                return None

        # Get all possible moves from current position
        possible_moves = self._get_valid_moves(classroom)
        if not possible_moves:
            return None

        self.last_move_time = current_time

        # Choose move based on strategy
        if self.strategy == MovementStrategy.CANDY_SEEKER:
            return self._find_nearest_candy_move(classroom, possible_moves)
        elif self.strategy == MovementStrategy.AVOIDANCE:
            return self._find_safest_move(classroom, possible_moves)
        elif self.strategy == MovementStrategy.DIRECTIONAL_BIAS:
            return self._find_directional_move(possible_moves)
        else:  # RANDOM_WALK
            return random.choice(possible_moves)

    def _get_valid_moves(self, classroom: 'Classroom') -> List[Position]:
        """
        Determines all valid moves from the current position.
        A valid move is within bounds and to an empty cell or candy.
        
        Args:
            classroom: The current state of the classroom environment
            
        Returns:
            List[Position]: List of all valid positions the child can move to
        """
        moves = []
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:  # Four cardinal directions
            new_x = self.position.x + dx
            new_y = self.position.y + dy
            if (0 <= new_x < classroom.width and 
                0 <= new_y < classroom.height and 
                classroom.grid[new_y][new_x] in [CellType.EMPTY, CellType.CANDY]):
                moves.append(Position(new_x, new_y))
        return moves

    def _find_nearest_candy_move(self, classroom: 'Classroom', possible_moves: List[Position]) -> Position:
        """
        Determines the best move to get closer to the nearest candy.
        
        Args:
            classroom: The current state of the classroom environment
            possible_moves: List of valid moves to choose from
            
        Returns:
            Position: The best move to get closer to candy, or a random move if no candy exists
        """
        candies = []
        for y in range(classroom.height):
            for x in range(classroom.width):
                if classroom.grid[y][x] == CellType.CANDY:
                    candies.append(Position(x, y))

        if not candies or not possible_moves:
            return random.choice(possible_moves) if possible_moves else None

        # Find the nearest candy
        nearest_candy = min(candies, key=lambda candy: self.position.distance_to(candy))
        
        # Choose the move that gets us closest to the nearest candy
        return min(possible_moves, key=lambda pos: pos.distance_to(nearest_candy))

    def _find_safest_move(self, classroom: 'Classroom', possible_moves: List[Position]) -> Position:
        """
        Determines the move that maximizes distance from the teacher.
        
        Args:
            classroom: The current state of the classroom environment
            possible_moves: List of valid moves to choose from
            
        Returns:
            Position: The move that puts most distance between child and teacher
        """
        if not possible_moves:
            return None
            
        teacher_pos = classroom.teacher.position if classroom.teacher else None
        if not teacher_pos:
            return random.choice(possible_moves)
            
        # Choose the move that maximizes distance from teacher
        return max(possible_moves, key=lambda pos: pos.distance_to(teacher_pos))

    def _find_directional_move(self, possible_moves: List[Position]) -> Position:
        """
        Determines move based on the child's preferred direction.
        
        Args:
            possible_moves: List of valid moves to choose from
            
        Returns:
            Position: Move in preferred direction if possible, otherwise random
        """
        # Try to move in preferred direction
        preferred_x = self.position.x + self.preferred_direction[0]
        preferred_y = self.position.y + self.preferred_direction[1]
        preferred_pos = Position(preferred_x, preferred_y)
        
        # Check if preferred move is possible
        for move in possible_moves:
            if move.x == preferred_x and move.y == preferred_y:
                return move
                
        # If can't move in preferred direction, choose random move
        return random.choice(possible_moves)