import numpy as np
from enum import Enum
import random
from typing import List, Tuple, Optional
import time

# Enums for representing different states and types in the simulation
class CellType(Enum):
    """Represents the different types of cells that can exist in the classroom grid"""
    EMPTY = 0      # An empty cell that agents can move into
    SAFE_ZONE = 1  # Part of the designated safe area, typically near teacher's desk
    CANDY = 2      # A candy that children can collect
    CHILD = 3      # A cell occupied by a child agent
    TEACHER = 4    # A cell occupied by the teacher agent

class AgentState(Enum):
    """Represents the possible states a child agent can be in"""
    FREE = 0       # Child is free to move and collect candy
    CAPTURED = 1   # Child has been caught by teacher and is being escorted

class MovementStrategy(Enum):
    """Different movement strategies that child agents can employ"""
    STRATEGIC_TIMING = 0  # Moves at specific time intervals
    AVOIDANCE = 1        # Tries to stay away from the teacher
    DIRECTIONAL_BIAS = 2 # Prefers moving in certain directions
    RANDOM_WALK = 3      # Moves randomly
    CANDY_SEEKER = 4     # Actively seeks out candy

class Position:
    """Represents a position in the classroom grid"""
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
    
    def distance_to(self, other: 'Position') -> float:
        """Calculates Euclidean distance to another position"""
        return np.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)
    
    def __eq__(self, other):
        """Enables position comparison with == operator"""
        if not isinstance(other, Position):
            return False
        return self.x == other.x and self.y == other.y

class Agent:
    """Base class for all agents in the simulation"""
    def __init__(self, position: Position):
        self.position = position
        self.previous_position = position  # Stores the last position for movement tracking

    def move(self, new_position: Position):
        """Updates agent position while keeping track of previous position"""
        self.previous_position = Position(self.position.x, self.position.y)
        self.position = new_position

class Child(Agent):
    """Represents a child agent in the simulation"""
    def __init__(self, position: Position, strategy: MovementStrategy):
        super().__init__(position)
        self.strategy = strategy
        self.state = AgentState.FREE
        self.last_move_time = time.time()
        self.move_cooldown = random.uniform(0.5, 2.0)  # Time between moves for strategic timing
        # For directional bias strategy
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
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:  # Four cardinal directions
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
        
        # Find the nearest candy
        for y in range(classroom.height):
            for x in range(classroom.width):
                if classroom.grid[y][x] == CellType.CANDY:
                    candy_pos = Position(x, y)
                    dist = self.position.distance_to(candy_pos)
                    if dist < min_distance:
                        min_distance = dist
                        nearest_candy = candy_pos

        if nearest_candy:
            # Choose the move that gets us closest to the candy
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
        # First try to move in preferred direction if possible
        preferred_x = self.position.x + self.preferred_direction[0]
        preferred_y = self.position.y + self.preferred_direction[1]
        preferred_pos = Position(preferred_x, preferred_y)
        
        for move in possible_moves:
            if move.x == preferred_x and move.y == preferred_y:
                return move
                
        # If can't move in preferred direction, choose random move
        return random.choice(possible_moves)

class Teacher(Agent):
    """Represents the teacher agent in the simulation"""
    def __init__(self, position: Position):
        super().__init__(position)
        self.escorting_child: Optional[Child] = None

    def choose_move(self, classroom: 'Classroom') -> Optional[Position]:
        """Determines teacher's next move based on current situation"""
        if self.escorting_child:
            return self._escort_to_safe_zone(classroom)
        return self._find_nearest_child_move(classroom)

    def _find_nearest_child_move(self, classroom: 'Classroom') -> Optional[Position]:
        """Finds best move to catch nearest free child"""
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
            
        # If adjacent to child, capture it
        if min_distance <= 1:
            return Position(nearest_child.position.x, nearest_child.position.y)
            
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
        if self.position.distance_to(nearest_safe) <= 1:
            self.escorting_child.state = AgentState.FREE
            self.escorting_child = None
            return None
            
        # Move toward safe zone
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

class Classroom:
    """Represents the classroom environment and manages the simulation"""
    def __init__(self, width: int, height: int, safe_zone_size: Tuple[int, int]):
        self.width = width
        self.height = height
        self.grid = np.full((height, width), CellType.EMPTY)
        self.safe_zone = self._initialize_safe_zone(safe_zone_size)
        self.children: List[Child] = []
        self.teacher: Optional[Teacher] = None
        self.last_candy_spawn = time.time()
        self.candy_spawn_interval = 10  # seconds between candy spawns

    def _initialize_safe_zone(self, size: Tuple[int, int]) -> List[Position]:
        """Sets up the safe zone area and returns list of safe zone positions"""
        safe_zone_positions = []
        for y in range(size[1]):
            for x in range(size[0]):
                self.grid[y][x] = CellType.SAFE_ZONE
                safe_zone_positions.append(Position(x, y))
        return safe_zone_positions

    def spawn_candy(self):
        """Spawns a new candy if enough time has passed since last spawn"""
        if time.time() - self.last_candy_spawn < self.candy_spawn_interval:
            return

        available_positions = [
            (x, y) for y in range(self.height) 
            for x in range(self.width) 
            if self.grid[y][x] == CellType.EMPTY
        ]
        
        if available_positions:
            x, y = random.choice(available_positions)
            self.grid[y][x] = CellType.CANDY
            self.last_candy_spawn = time.time()

    def update(self):
        """Main simulation step that updates all agents and environment"""
        # Spawn new candy if needed
        self.spawn_candy()
        
        # Update children
        for child in self.children:
            if child.state == AgentState.FREE:
                new_position = child.choose_move(self)
                if new_position:
                    self._update_agent_position(child, new_position)
                    
                    # Check if child reached candy
                    if self.grid[new_position.y][new_position.x] == CellType.CANDY:
                        self.grid[new_position.y][new_position.x] = CellType.EMPTY

        # Update teacher
        if self.teacher:
            new_position = self.teacher.choose_move(self)
            if new_position:
                # Check if teacher is catching a child
                for child in self.children:
                    if (child.state == AgentState.FREE and 
                        child.position.x == new_position.x and 
                        child.position.y == new_position.y):
                        child.state = AgentState.CAPTURED
                        self.teacher.escorting_child = child
                        
                self._update_agent_position(self.teacher, new_position)

    def _update_agent_position(self, agent: Agent, new_position: Position):
        """Updates agent position in the grid"""
        # Clear old position
        self.grid[agent.position.y][agent.position.x] = CellType.EMPTY
        
        # Update to new position
        self.grid[new_position.y][new_position.x] = (
            CellType.TEACHER if isinstance(agent, Teacher) else CellType.CHILD
        )
        agent.move(new_position)

    def print_state(self):
        """Prints current state of the classroom grid (useful for debugging)"""
        symbol_map = {
            CellType.EMPTY: '.',
            CellType.SAFE_ZONE: 'S',
            CellType.CANDY: 'C',
            CellType.CHILD: 'K',
            CellType.TEACHER: 'T'
        }
        
        for row in self.grid:
            print(' '.join(symbol_map[cell] for cell in row))
        print()

def main():
    """Example usage of the classroom simulation"""
    # Initialize classroom
    classroom = Classroom(width=10, height=10, safe_zone_size=(3, 3))
    
    # Add teacher
    teacher = Teacher(Position(5, 5))
    classroom.teacher = teacher
    classroom.grid[5][5] = CellType.TEACHER
    
    # Add children with different strategies
    child_positions = [(1, 1), (8, 8), (3, 7)]
    strategies = [
        MovementStrategy.RANDOM_WALK,
        MovementStrategy.CANDY_SEEKER,
        MovementStrategy.AVOIDANCE
    ]
    
    for pos, strategy in zip(child_positions, strategies):
        child = Child(Position(pos[0], pos[1]), strategy)
        classroom.children.append(child)
        classroom.grid[pos[1]][pos[0]] = CellType.CHILD
    
    # Run simulation for 50 steps
    for _ in range(50):
        classroom.update()
        classroom.print_state()
        time.sleep(0.5)  # Add delay to make it visible

if __name__ == "__main__":
    main()