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
        
        for child in self.children:
            if child.state == AgentState.FREE:
                new_position = child.choose_move(self)
                if new_position:
                    self._update_agent_position(child, new_position)
                    
                    if self.grid[new_position.y][new_position.x] == CellType.CANDY:
                        self.grid[new_position.y][new_position.x] = CellType.EMPTY

        if self.teacher:
            new_position = self.teacher.choose_move(self)
            if new_position:
                for child in self.children:
                    if (child.state == AgentState.FREE and 
                        child.position.x == new_position.x and 
                        child.position.y == new_position.y):
                        child.state = AgentState.CAPTURED
                        self.teacher.escorting_child = child
                        
                self._update_agent_position(self.teacher, new_position)

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