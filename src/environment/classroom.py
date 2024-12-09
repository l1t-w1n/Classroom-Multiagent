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
    """Represents the classroom environment and manages the simulation"""
    def __init__(self, width: int, height: int, safe_zone_size: Tuple[int, int]):
        self.width = width
        self.height = height
        self.grid = np.full((height, width), CellType.EMPTY)
        self.safe_zone = self._initialize_safe_zone(safe_zone_size)
        self.children: List[Child] = []
        self.teacher: Optional[Teacher] = None
        self.last_candy_spawn = time.time()
        self.candy_spawn_interval = 10

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
        self.spawn_candy()
        
        # Update free children
        for child in self.children:
            if child.state == AgentState.FREE:
                new_position = child.choose_move(self)
                if new_position:
                    # Check if there's candy at the new position
                    if self.grid[new_position.y][new_position.x] == CellType.CANDY:
                        # Collect candy when moving onto it
                        self.grid[new_position.y][new_position.x] = CellType.EMPTY
                    
                    # Update old position
                    self.grid[child.position.y][child.position.x] = CellType.EMPTY
                    # Move child
                    child.move(new_position)
                    # Update new position
                    self.grid[new_position.y][new_position.x] = CellType.CHILD

        # Update teacher
        if self.teacher:
            new_position = self.teacher.choose_move(self)
            if new_position:
                # Check if the new position has a free child (for capture)
                has_child = False
                captured_child = None
                for child in self.children:
                    if (child.state == AgentState.FREE and 
                        child.position.x == new_position.x and 
                        child.position.y == new_position.y):
                        has_child = True
                        captured_child = child
                        break

                # If moving to a child's position, capture the child
                if has_child and captured_child:
                    captured_child.state = AgentState.CAPTURED
                    self.teacher.escorting_child = captured_child
                    
                # Only move if the new position is empty or has a capturable child
                if self.grid[new_position.y][new_position.x] in [CellType.EMPTY, CellType.CHILD]:
                    # Update old position
                    self.grid[self.teacher.position.y][self.teacher.position.x] = CellType.EMPTY
                    self.teacher.move(new_position)
                    self.grid[new_position.y][new_position.x] = CellType.TEACHER
                    
                    # If escorting a child, update its position too
                    if self.teacher.escorting_child:
                        self.teacher.escorting_child.move(new_position)

    def _update_agent_position(self, agent: Agent, new_position: Position):
        """Updates agent position in the grid"""
        self.grid[agent.position.y][agent.position.x] = CellType.EMPTY
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