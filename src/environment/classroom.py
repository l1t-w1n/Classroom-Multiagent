import numpy as np
import random
import time
from typing import List, Tuple, Optional

from ..position import Position
from ..enums import CellType, AgentState
from ..agents.teacher import Teacher
from ..agents.child import Child
from ..agents.base_agent import Agent

class Classroom:
    """
    Represents the classroom environment and manages the simulation.
    The classroom contains a grid where children move around collecting candies
    while avoiding the teacher. When the teacher gets adjacent to a child,
    the child is immediately teleported to the safe zone.
    """
    def __init__(self, width: int, height: int, safe_zone_size: Tuple[int, int]):
        """
        Initializes the classroom environment with specified dimensions.
        
        Args:
            width: The width of the classroom grid
            height: The height of the classroom grid
            safe_zone_size: Tuple of (width, height) for the safe zone area
        """
        self.width = width
        self.height = height
        self.grid = np.full((height, width), CellType.EMPTY)
        self.safe_zone = self._initialize_safe_zone(safe_zone_size)
        self.children: List[Child] = []
        self.teacher: Optional[Teacher] = None
        self.last_candy_spawn = time.time()
        self.candy_spawn_interval = 10

    def _initialize_safe_zone(self, size: Tuple[int, int]) -> List[Position]:
        """
        Sets up the safe zone area in the top-left corner of the classroom.
        
        Args:
            size: Tuple of (width, height) for the safe zone
            
        Returns:
            List of Position objects representing safe zone coordinates
        """
        safe_zone_positions = []
        for y in range(size[1]):
            for x in range(size[0]):
                self.grid[y][x] = CellType.SAFE_ZONE
                safe_zone_positions.append(Position(x, y))
        return safe_zone_positions

    def spawn_candy(self):
        """
        Spawns a new candy in a random empty cell if enough time has passed.
        Candies will not spawn in the safe zone or on occupied cells.
        """
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
        """
        Main simulation step that updates all agents and environment.
        Handles candy spawning, child movement, candy collection,
        and teacher movement with child teleportation.
        """
        self.spawn_candy()
        
        # First, handle teacher movement and potential teleportation
        if self.teacher:
            # Check if teacher is adjacent to any child before moving
            for child in self.children:
                if child.can_move() and self.teacher.is_adjacent_to(child.position):
                    # Find nearest safe zone position
                    nearest_safe = min(self.safe_zone,
                                    key=lambda pos: child.position.distance_to(pos))
                    
                    # Clear child's old position
                    self.grid[child.position.y][child.position.x] = CellType.EMPTY
                    
                    # Move child to safe zone
                    child.position = nearest_safe
                    self.grid[nearest_safe.y][nearest_safe.x] = CellType.CHILD
                    
                    # Set cooldown on the child
                    child.set_cooldown(10.0)
                    
                    # Don't process teacher movement this turn
                    break
            else:  # Only move teacher if no adjacent children were found
                new_position = self.teacher.choose_move(self)
                if new_position:
                    self.grid[self.teacher.position.y][self.teacher.position.x] = CellType.EMPTY
                    self.teacher.move(new_position)
                    self.grid[new_position.y][new_position.x] = CellType.TEACHER
        
        # Then update children that aren't in cooldown
        for child in self.children:
            if child.can_move():
                new_position = child.choose_move(self)
                if new_position:
                    # Collect candy if present at new position
                    if self.grid[new_position.y][new_position.x] == CellType.CANDY:
                        self.grid[new_position.y][new_position.x] = CellType.EMPTY
                    
                    # Update child's position
                    self.grid[child.position.y][child.position.x] = CellType.EMPTY
                    child.move(new_position)
                    self.grid[new_position.y][new_position.x] = CellType.CHILD

    def print_state(self):
        """
        Prints a text representation of the current classroom state.
        Useful for debugging and console visualization.
        
        Symbol legend:
        . - Empty cell
        S - Safe zone
        C - Candy
        K - Child
        T - Teacher
        """
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