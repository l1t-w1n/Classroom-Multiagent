from typing import List, Optional
import random
import time
from .base_agent import Agent
from ..position import Position
from ..enums import AgentState, MovementStrategy, CellType

class Child(Agent):
    """
    Represents a child agent in the simulation that moves around collecting candies while avoiding teachers.
    Each child uses a specific movement strategy and can be temporarily immobilized by cooldown periods.
    """
    def __init__(self, position: Position, strategy: MovementStrategy):
        super().__init__(position)
        self.strategy = strategy
        self.state = AgentState.FREE
        self.cooldown_until = 0
        self.last_move_time = time.time()
        self.move_cooldown = random.uniform(0.5, 2.0)
        self.candys_eaten = 0
        
        # For directional bias strategy
        self.preferred_direction = random.choice([(0, 1), (1, 0), (0, -1), (-1, 0)])
        
        # For unpredictable strategy
        self.current_substrategy = MovementStrategy.RANDOM_WALK
        self.strategy_switch_time = time.time() + random.uniform(5.0, 10.0)

    def choose_move(self, classroom: 'Classroom') -> Optional[Position]:
        """
        Determines the next move based on the child's strategy and current classroom state.
        Considers multiple teachers when making movement decisions.
        """
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

        if self.strategy == MovementStrategy.UNPREDICTABLE:
            if current_time >= self.strategy_switch_time:
                # Choose any strategy except unpredictable to avoid recursion
                self.current_substrategy = random.choice([
                    strat for strat in MovementStrategy 
                    if strat != MovementStrategy.UNPREDICTABLE
                ])
                self.strategy_switch_time = current_time + random.uniform(5.0, 10.0)
            return self._execute_strategy(self.current_substrategy, classroom, possible_moves)

        return self._execute_strategy(self.strategy, classroom, possible_moves)

    def _execute_strategy(self, strategy: MovementStrategy, classroom: 'Classroom', 
                         possible_moves: List[Position]) -> Position:
        """Maps each strategy to its corresponding movement function."""
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

    def _get_valid_moves(self, classroom: 'Classroom') -> List[Position]:
        """Determines all valid moves from the current position."""
        moves = []
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            new_x = self.position.x + dx
            new_y = self.position.y + dy
            if (0 <= new_x < classroom.width and 
                0 <= new_y < classroom.height and 
                classroom.grid[new_y][new_x] in [CellType.EMPTY, CellType.CANDY]):
                moves.append(Position(new_x, new_y))
        return moves

    def _find_safest_move(self, classroom: 'Classroom', possible_moves: List[Position]) -> Position:
        """
        Finds the safest move considering all teachers' positions.
        Calculates a danger score for each possible move based on proximity to all teachers.
        """
        if not possible_moves:
            return None
            
        def calculate_danger_score(pos: Position) -> float:
            """Calculate total danger from all teachers, weighted by distance."""
            danger_score = 0
            for teacher in classroom.teachers:
                distance = pos.distance_to(teacher.position)
                # Closer teachers contribute more to the danger score
                danger_score += 1 / (distance + 1)  # Add 1 to avoid division by zero
            return danger_score

        # Choose the move with the lowest total danger score
        return min(possible_moves, key=calculate_danger_score)

    def _find_nearest_candy_move(self, classroom: 'Classroom', possible_moves: List[Position]) -> Position:
        """Moves toward the nearest candy while considering teacher positions."""
        candies = []
        for y in range(classroom.height):
            for x in range(classroom.width):
                if classroom.grid[y][x] == CellType.CANDY:
                    candies.append(Position(x, y))

        if not candies or not possible_moves:
            return random.choice(possible_moves)

        def calculate_candy_score(pos: Position, candy: Position) -> float:
            """Score considers both candy distance and teacher proximity."""
            candy_distance = pos.distance_to(candy)
            teacher_danger = sum(1 / (pos.distance_to(t.position) + 1) 
                               for t in classroom.teachers)
            return candy_distance + (teacher_danger * 2)  # Weight teacher danger more heavily

        # Find best candy considering both distance and safety
        best_candy = min(candies, key=lambda c: calculate_candy_score(self.position, c))
        return min(possible_moves, key=lambda pos: pos.distance_to(best_candy))

    def _find_wall_hugging_move(self, classroom: 'Classroom', possible_moves: List[Position]) -> Position:
        """Finds moves that keep the child close to walls while avoiding teachers."""
        def wall_score(pos: Position) -> float:
            # Calculate wall proximity
            wall_proximity = min(
                pos.x, pos.y,
                classroom.width - 1 - pos.x,
                classroom.height - 1 - pos.y
            )
            return wall_proximity  # Negative because we want to minimize

        return min(possible_moves, key=wall_score)

    def _find_group_move(self, classroom: 'Classroom', possible_moves: List[Position]) -> Position:
        """Moves toward other children while maintaining safe distance from teachers."""
        def group_score(pos: Position) -> float:
            # Count nearby children
            child_score = sum(1 for child in classroom.children
                            if child != self and child.state == AgentState.FREE
                            and pos.distance_to(child.position) <= 3)
            # Calculate teacher danger
            teacher_danger = sum(1 / (pos.distance_to(t.position) + 1) 
                               for t in classroom.teachers)
            return child_score - (teacher_danger * 2)

        return max(possible_moves, key=group_score)

    def _find_candy_rich_area_move(self, classroom: 'Classroom', possible_moves: List[Position]) -> Position:
        """Targets areas with multiple candies while avoiding teachers."""
        def area_score(pos: Position) -> float:
            candy_count = 0
            for y in range(max(0, pos.y - 3), min(classroom.height, pos.y + 4)):
                for x in range(max(0, pos.x - 3), min(classroom.width, pos.x + 4)):
                    if classroom.grid[y][x] == CellType.CANDY:
                        candy_count += 1
            
            teacher_danger = sum(1 / (pos.distance_to(t.position) + 1) 
                               for t in classroom.teachers)
            return candy_count - (teacher_danger * 2)

        return max(possible_moves, key=area_score)

    def _find_safe_exploration_move(self, classroom: 'Classroom', possible_moves: List[Position]) -> Position:
        """Alternates between safe zone proximity and exploration, considering teacher positions."""
        time_since_cooldown = time.time() - self.cooldown_until
        exploration_phase = (time_since_cooldown % 20) > 10

        if exploration_phase:
            return self._find_nearest_candy_move(classroom, possible_moves)
        else:
            nearest_safe = min(classroom.safe_zone,
                             key=lambda pos: self.position.distance_to(pos))
            return min(possible_moves,
                      key=lambda pos: pos.distance_to(nearest_safe))

    def _find_directional_move(self, possible_moves: List[Position]) -> Position:
        """Maintains directional preference when possible."""
        preferred_x = self.position.x + self.preferred_direction[0]
        preferred_y = self.position.y + self.preferred_direction[1]
        
        for move in possible_moves:
            if move.x == preferred_x and move.y == preferred_y:
                return move
        return random.choice(possible_moves)

    def set_cooldown(self, duration: float):
        """Sets a cooldown period during which the child cannot move."""
        self.cooldown_until = time.time() + duration

    def can_move(self) -> bool:
        """Checks if the child is allowed to move."""
        return time.time() >= self.cooldown_until