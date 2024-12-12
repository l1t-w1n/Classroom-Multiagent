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
    while avoiding multiple teachers. When a teacher gets adjacent to a child,
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
        # Initialize basic grid properties
        self.width = width
        self.height = height
        self.grid = np.full((height, width), CellType.EMPTY)
        
        # Initialize the safe zone and get its positions
        self.safe_zone = self._initialize_safe_zone(safe_zone_size)
        
        # Lists to track all agents in the classroom
        self.children: List[Child] = []
        self.teachers: List[Teacher] = []
        
        # Candy spawning properties
        self.last_candy_spawn = time.time()
        self.candy_spawn_interval = 3  # Seconds between candy spawns

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
        Spawns a new candy in a random empty cell if the candy limit hasn't been reached.
        The maximum number of candies allowed on the board at any time is 5.
        Candies will not spawn in the safe zone or on occupied cells.
        """
        # Count the number of candies currently on the board
        candy_count = np.count_nonzero(self.grid == CellType.CANDY)
        
        # Check if the candy limit has been reached
        if candy_count >= 5:
            return  # Exit the method without spawning any new candies
        
        if time.time() - self.last_candy_spawn < self.candy_spawn_interval:
            return

        # Find all empty cells where candy can spawn
        available_positions = [
            (x, y) for y in range(self.height) 
            for x in range(self.width) 
            if self.grid[y][x] == CellType.EMPTY
        ]
        
        if available_positions:
            x, y = random.choice(available_positions)
            self.grid[y][x] = CellType.CANDY
            self.last_candy_spawn = time.time()

    def _process_teacher_movement(self, teacher: Teacher):
        """
        Processes a single teacher's movement and any resulting interactions.
        This includes checking for adjacent children and handling teleportation.
        
        Args:
            teacher: The teacher whose movement is being processed
        """
        # First check if teacher is adjacent to any children
        for child in self.children:
            if child.can_move() and teacher.is_adjacent_to(child.position):
                # Find nearest safe zone position for teleportation
                nearest_safe = min(self.safe_zone,
                                key=lambda pos: child.position.distance_to(pos))
                
                # Update grid, preserving safe zone status where needed
                old_x, old_y = child.position.x, child.position.y
                self.grid[old_y][old_x] = (CellType.SAFE_ZONE 
                    if any(old_x == sz.x and old_y == sz.y for sz in self.safe_zone)
                    else CellType.EMPTY)
                
                # Teleport child and apply cooldown
                child.position = nearest_safe
                self.grid[nearest_safe.y][nearest_safe.x] = CellType.CHILD
                child.set_cooldown(5.0)
                return  # Exit after handling one teleportation

        # If no teleportation occurred, try to move teacher
        new_position = teacher.choose_move(self)
        if new_position:
            # Update teacher position while preserving safe zone
            old_x, old_y = teacher.position.x, teacher.position.y
            self.grid[old_y][old_x] = (CellType.SAFE_ZONE 
                if any(old_x == sz.x and old_y == sz.y for sz in self.safe_zone)
                else CellType.EMPTY)
            
            teacher.move(new_position)
            self.grid[new_position.y][new_position.x] = CellType.TEACHER

    def update(self):
        """
        Main simulation step that updates all agents and environment.
        The update sequence is:
        1. Spawn new candies if needed
        2. First teacher movement opportunity
        3. Children movement
        4. Second teacher movement opportunity
        This gives teachers a speed advantage while maintaining fairness.
        """
        # Spawn new candies if it's time
        self.spawn_candy()
        
        # First movement opportunity for all teachers
        for teacher in self.teachers:
            self._process_teacher_movement(teacher)

        # Update all children that aren't in cooldown
        for child in self.children:
            if child.can_move():
                new_position = child.choose_move(self)
                if new_position:
                    # Handle candy collection if moving to candy cell
                    if self.grid[new_position.y][new_position.x] == CellType.CANDY:
                        self.grid[new_position.y][new_position.x] = CellType.EMPTY
                    
                    # Update child's position while preserving safe zone
                    old_x, old_y = child.position.x, child.position.y
                    self.grid[old_y][old_x] = (CellType.SAFE_ZONE 
                        if any(old_x == sz.x and old_y == sz.y for sz in self.safe_zone)
                        else CellType.EMPTY)
                    child.move(new_position)
                    self.grid[new_position.y][new_position.x] = CellType.CHILD

        # Second movement opportunity for all teachers
        for teacher in self.teachers:
            self._process_teacher_movement(teacher)

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

    def is_position_safe_zone(self, x: int, y: int) -> bool:
        """
        Checks if a given position is within the safe zone.
        
        Args:
            x: X coordinate to check
            y: Y coordinate to check
            
        Returns:
            bool: True if position is in safe zone, False otherwise
        """
        return any(x == sz.x and y == sz.y for sz in self.safe_zone)