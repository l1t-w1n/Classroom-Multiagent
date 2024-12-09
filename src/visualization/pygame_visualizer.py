import pygame
import sys
from typing import Dict, Tuple
from ..enums import CellType
from ..environment.classroom import Classroom

class ClassroomVisualizer:
    """Handles the graphical visualization of the classroom simulation using Pygame"""
    
    def __init__(self, classroom: Classroom, cell_size: int = 40):
        """
        Initialize the visualization system.
        
        Args:
            classroom: The classroom environment to visualize
            cell_size: Size of each grid cell in pixels
        """
        pygame.init()
        
        # Calculate window dimensions based on grid size
        self.cell_size = cell_size
        self.width = classroom.width * cell_size
        self.height = classroom.height * cell_size
        
        # Set up the display window
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Classroom Simulation")
        
        # Define colors for different cell types
        self.colors = {
            CellType.EMPTY: (255, 255, 255),     # White
            CellType.SAFE_ZONE: (200, 230, 200), # Light green
            CellType.CANDY: (255, 182, 193),     # Light pink
            CellType.CHILD: (135, 206, 235),     # Sky blue
            CellType.TEACHER: (255, 140, 0)      # Dark orange
        }
        
        # For smooth animation
        self.clock = pygame.time.Clock()
        self.FPS = 2

    def draw_grid(self, classroom: Classroom):
        """
        Draw the classroom grid with all its elements.
        
        Args:
            classroom: Current state of the classroom to render
        """
        # Fill background
        self.screen.fill((240, 240, 240))  # Light gray background
        
        # Draw each cell
        for y in range(classroom.height):
            for x in range(classroom.width):
                cell_type = classroom.grid[y][x]
                color = self.colors[cell_type]
                
                # Calculate pixel coordinates
                rect = pygame.Rect(
                    x * self.cell_size,
                    y * self.cell_size,
                    self.cell_size,
                    self.cell_size
                )
                
                # Draw cell
                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, (200, 200, 200), rect, 1)  # Grid lines
                
                # Add visual indicators for agents
                if cell_type in [CellType.CHILD, CellType.TEACHER]:
                    # Draw a circle inside the cell
                    center = (
                        x * self.cell_size + self.cell_size // 2,
                        y * self.cell_size + self.cell_size // 2
                    )
                    radius = self.cell_size // 3
                    pygame.draw.circle(self.screen, (0, 0, 0), center, radius)
                elif cell_type == CellType.CANDY:
                    # Draw a diamond shape for candy
                    center_x = x * self.cell_size + self.cell_size // 2
                    center_y = y * self.cell_size + self.cell_size // 2
                    size = self.cell_size // 3
                    points = [
                        (center_x, center_y - size),  # Top
                        (center_x + size, center_y),  # Right
                        (center_x, center_y + size),  # Bottom
                        (center_x - size, center_y)   # Left
                    ]
                    pygame.draw.polygon(self.screen, (255, 0, 0), points)

    def show_status(self, classroom: Classroom):
        """
        Display simulation statistics on screen.
        
        Args:
            classroom: Current classroom state
        """
        # Create a font object
        font = pygame.font.Font(None, 24)
        
        # Count various elements
        free_children = sum(1 for child in classroom.children if child.state.FREE)
        captured_children = len(classroom.children) - free_children
        candies = sum(1 for row in classroom.grid for cell in row if cell == CellType.CANDY)
        
        # Create status text
        status_lines = [
            f"Free Children: {free_children}",
            f"Captured: {captured_children}",
            f"Candies: {candies}"
        ]
        
        # Render each line
        for i, line in enumerate(status_lines):
            text = font.render(line, True, (0, 0, 0))
            self.screen.blit(text, (10, 10 + i * 25))

    def handle_events(self) -> bool:
        """
        Handle Pygame events.
        
        Returns:
            bool: False if the simulation should end, True otherwise
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
        return True

    def update(self, classroom: Classroom) -> bool:
        """
        Update the visualization for one frame.
        
        Args:
            classroom: Current classroom state
        
        Returns:
            bool: False if the simulation should end, True otherwise
        """
        # Handle events
        if not self.handle_events():
            pygame.quit()
            return False
        
        # Draw everything
        self.draw_grid(classroom)
        self.show_status(classroom)
        
        # Update display
        pygame.display.flip()
        
        # Control frame rate
        self.clock.tick(self.FPS)
        return True

    def cleanup(self):
        """Clean up Pygame resources"""
        pygame.quit()