import pygame
import math
import sys
from typing import Dict, Tuple
from ..enums import CellType, MovementStrategy
from ..config.config_manager import ConfigManager
from ..environment.classroom import Classroom

class ClassroomVisualizer:
    """Handles the graphical visualization of the classroom simulation using Pygame"""
    
    def __init__(self, classroom: Classroom, cell_size: int = 40):
        pygame.init()
        
        # Store reference to classroom for accessing safe zone
        self.classroom = classroom
        self.cell_size = cell_size
        self.grid_width = classroom.width * cell_size
        
        # Increase legend width to accommodate additional information
        self.legend_width = 350  # Made wider for teacher count
        self.width = self.grid_width + self.legend_width
        self.height = max(classroom.height * cell_size, 400)
        
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Multi-Teacher Classroom Simulation")
        
        # Base colors for different cell types
        self.colors = {
            CellType.EMPTY: (255, 255, 255),     # White
            CellType.SAFE_ZONE: (200, 230, 200), # Light green
            CellType.CANDY: (255, 182, 193),     # Light pink
            CellType.TEACHER: (255, 140, 0),     # Dark orange
            CellType.CHILD: (135, 206, 235)      # Default child color (sky blue)
        }
        
        # Strategy-specific colors and shapes for children
        self.strategy_styles = {
            MovementStrategy.RANDOM_WALK: {
                'color': (135, 206, 235),  # Sky blue
                'shape': 'circle'
            },
            MovementStrategy.CANDY_SEEKER: {
                'color': (255, 105, 180),  # Hot pink
                'shape': 'triangle'
            },
            MovementStrategy.AVOIDANCE: {
                'color': (50, 205, 50),    # Lime green
                'shape': 'diamond'
            },
            MovementStrategy.DIRECTIONAL_BIAS: {
                'color': (238, 130, 238),  # Violet
                'shape': 'square'
            },
            MovementStrategy.STRATEGIC_TIMING: {
                'color': (255, 215, 0),    # Gold
                'shape': 'pentagon'
            },
            MovementStrategy.WALL_HUGGER: {
                'color': (165, 42, 42),    # Brown
                'shape': 'star'
            },
            MovementStrategy.GROUP_SEEKER: {
                'color': (70, 130, 180),   # Steel blue
                'shape': 'hexagon'
            },
            MovementStrategy.CANDY_HOARDER: {
                'color': (255, 99, 71),    # Tomato
                'shape': 'cross'
            },
            MovementStrategy.SAFE_EXPLORER: {
                'color': (147, 112, 219),  # Medium purple
                'shape': 'octagon'
            },
            MovementStrategy.UNPREDICTABLE: {
                'color': (128, 128, 128),  # Gray
                'shape': 'ring'
            }
        }
        self.config = ConfigManager()
        self.clock = pygame.time.Clock()
        self.FPS = self.config.fps
        
    def draw_right_panel(self):
        """
        Draws the complete right panel including status counters and strategy legend.
        Organizes information in a clear, hierarchical way.
        """
        legend_x = self.grid_width +10
        legend_y = 20
        font = pygame.font.Font(None, 24)
        
        # First, draw a panel background for better visibility
        panel_rect = pygame.Rect(self.grid_width, 0, self.legend_width, self.height)
        pygame.draw.rect(self.screen, (220, 220, 220), panel_rect)
        
        # Draw title for Statistics section
        title = font.render("Simulation Statistics", True, (0, 0, 0))
        self.screen.blit(title, (legend_x, legend_y))
        legend_y += 30
        
        # Calculate statistics
        active_children = sum(1 for child in self.classroom.children if child.can_move())
        on_cooldown = len(self.classroom.children) - active_children
        candies = sum(1 for row in self.classroom.grid 
                    for cell in row if cell == CellType.CANDY)
        
        # Count children and candies by strategy
        strategy_counts = {}
        strategy_candy_counts = {}
        for strategy in MovementStrategy:
            strategy_counts[strategy] = 0
            strategy_candy_counts[strategy] = 0
        
        for child in self.classroom.children:
            strategy_counts[child.strategy] += 1
            strategy_candy_counts[child.strategy] += child.candys_eaten
        
        # Draw main statistics with enhanced visibility
        stats_lines = [
            ("Total Children", len(self.classroom.children)),
            ("Active Children", active_children),
            ("On Cooldown", on_cooldown),
            ("Active Teachers", len(self.classroom.teachers)),
            ("Current Candies", candies)
        ]
        
        # Draw each statistic line
        for label, value in stats_lines:
            # Draw background highlight for better readability
            highlight_rect = pygame.Rect(legend_x - 5, legend_y - 2,
                                        self.legend_width - 10, 25)
            pygame.draw.rect(self.screen, (200, 200, 200), highlight_rect)
            
            # Draw the statistics text
            text = font.render(f"{label}: {value}", True, (0, 0, 0))
            self.screen.blit(text, (legend_x, legend_y))
            legend_y += 30
        
        # Add some spacing before strategy legend
        legend_y += 20
        
        # Draw Strategy Legend title
        title = font.render("Strategy Legend", True, (0, 0, 0))
        self.screen.blit(title, (legend_x, legend_y))
        legend_y += 30
        
        # Draw each strategy with its count and candies eaten
        for strategy in MovementStrategy:
            style = self.strategy_styles[strategy]
            
            # Draw strategy shape
            self.draw_shape(
                self.screen,
                style['shape'],
                (legend_x + 15, legend_y + 10),
                20,
                style['color']
            )
            
            # Create strategy name with count and candies eaten
            strategy_text = (f"{strategy.name.replace('_', ' ').title()}"
                            f"(Count: {strategy_counts[strategy]}, "
                            f"Candies: {strategy_candy_counts[strategy]})")
            
            # Draw text with shadow for better readability
            shadow = font.render(strategy_text, True, (50, 50, 50))
            self.screen.blit(shadow, (legend_x + 36, legend_y + 1))
            text = font.render(strategy_text, True, (0, 0, 0))
            self.screen.blit(text, (legend_x + 35, legend_y))
            
            legend_y += 25
                
    def get_cell_color(self, x: int, y: int, cell_type: CellType) -> Tuple[int, int, int]:
        """
        Determines the color for a cell based on its type and position.
        Ensures safe zone cells maintain their color even when empty.
        
        Args:
            x: X coordinate of the cell
            y: Y coordinate of the cell
            cell_type: Type of the cell (EMPTY, SAFE_ZONE, etc.)
        
        Returns:
            Tuple of RGB values representing the cell's color
        """
        # Check if the cell is in the safe zone
        is_safe_zone = any(x == sz.x and y == sz.y for sz in self.classroom.safe_zone)
        
        # If it's in safe zone, always return safe zone color
        if is_safe_zone:
            return self.colors[CellType.SAFE_ZONE]
        
        # Otherwise return the color for the cell type
        return self.colors[cell_type]

    # Complete the shape drawing methods by adding the missing shapes:
    def draw_shape(self, surface, shape: str, center: Tuple[int, int], size: int, color: Tuple[int, int, int]):
        """Draw different shapes based on strategy"""
        x, y = center
        if shape == 'circle':
            pygame.draw.circle(surface, color, center, size//2)
        elif shape == 'triangle':
            points = [(x, y - size//2), (x - size//2, y + size//2), (x + size//2, y + size//2)]
            pygame.draw.polygon(surface, color, points)
        elif shape == 'diamond':
            points = [(x, y - size//2), (x + size//2, y), (x, y + size//2), (x - size//2, y)]
            pygame.draw.polygon(surface, color, points)
        elif shape == 'square':
            rect = pygame.Rect(x - size//2, y - size//2, size, size)
            pygame.draw.rect(surface, color, rect)
        elif shape == 'pentagon':
            points = [(x, y - size//2), (x + size//2, y - size//6), 
                     (x + size//3, y + size//2), (x - size//3, y + size//2),
                     (x - size//2, y - size//6)]
            pygame.draw.polygon(surface, color, points)
        elif shape == 'star':
            # Draw a five-pointed star
            points = []
            for i in range(5):
                # Outer points
                angle = -90 + i * 72  # Start from top, go clockwise
                rad = math.radians(angle)
                points.append((x + size//2 * math.cos(rad), y + size//2 * math.sin(rad)))
                # Inner points
                angle += 36
                rad = math.radians(angle)
                points.append((x + size//4 * math.cos(rad), y + size//4 * math.sin(rad)))
            pygame.draw.polygon(surface, color, points)
        elif shape == 'hexagon':
            points = []
            for i in range(6):
                angle = i * 60
                rad = math.radians(angle)
                points.append((x + size//2 * math.cos(rad), y + size//2 * math.sin(rad)))
            pygame.draw.polygon(surface, color, points)
        elif shape == 'cross':
            # Draw a plus sign
            pygame.draw.rect(surface, color, (x - size//6, y - size//2, size//3, size))
            pygame.draw.rect(surface, color, (x - size//2, y - size//6, size, size//3))
        elif shape == 'octagon':
            points = []
            for i in range(8):
                angle = i * 45
                rad = math.radians(angle)
                points.append((x + size//2 * math.cos(rad), y + size//2 * math.sin(rad)))
            pygame.draw.polygon(surface, color, points)
        elif shape == 'ring':
            pygame.draw.circle(surface, color, center, size//2)      # Outer circle
            pygame.draw.circle(surface, (240, 240, 240), center, size//3)  # Inner circle (creates ring effect)

    def draw_legend(self):
        """Draw legend showing different strategies"""
        legend_x = self.grid_width + 10
        legend_y = 10
        font = pygame.font.Font(None, 24)
        
        # Draw legend title
        title = font.render("Strategy Legend", True, (0, 0, 0))
        self.screen.blit(title, (legend_x, legend_y))
        legend_y += 30
        
        # Draw each strategy in legend
        for strategy in MovementStrategy:
            style = self.strategy_styles[strategy]
            # Draw strategy shape
            self.draw_shape(self.screen, style['shape'], 
                          (legend_x + 15, legend_y + 10), 
                          20, style['color'])
            # Draw strategy name
            text = font.render(strategy.name.replace('_', ' ').title(), 
                             True, (0, 0, 0))
            self.screen.blit(text, (legend_x + 35, legend_y))
            legend_y += 25

    def draw_grid(self, classroom: Classroom):
        """
        Draw the classroom grid with support for multiple teachers.
        """
        self.screen.fill((240, 240, 240))
        
        # Draw base grid
        for y in range(classroom.height):
            for x in range(classroom.width):
                cell_type = classroom.grid[y][x]
                color = self.get_cell_color(x, y, cell_type)
                
                rect = pygame.Rect(
                    x * self.cell_size,
                    y * self.cell_size,
                    self.cell_size,
                    self.cell_size
                )
                
                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, (200, 200, 200), rect, 1)
                
                center = (
                    x * self.cell_size + self.cell_size // 2,
                    y * self.cell_size + self.cell_size // 2
                )
                
                # Draw different entities
                if cell_type == CellType.TEACHER:
                    # Draw teachers with a distinctive appearance
                    size = self.cell_size // 3
                    pygame.draw.circle(self.screen, self.colors[CellType.TEACHER], 
                                    center, size)
                    # Add an inner circle for better visibility
                    pygame.draw.circle(self.screen, (255, 200, 150), 
                                    center, size // 2)
                    
                elif cell_type == CellType.CHILD:
                    # Find and draw the child with its strategy-specific appearance
                    for child in classroom.children:
                        if child.position.x == x and child.position.y == y:
                            style = self.strategy_styles[child.strategy]
                            self.draw_shape(self.screen, style['shape'], center,
                                          self.cell_size // 2, style['color'])
                            break
                            
                elif cell_type == CellType.CANDY:
                    # Draw candy
                    size = self.cell_size // 3
                    points = [
                        (center[0], center[1] - size),
                        (center[0] + size, center[1]),
                        (center[0], center[1] + size),
                        (center[0] - size, center[1])
                    ]
                    pygame.draw.polygon(self.screen, (255, 0, 0), points)
        
        # Draw legend after grid
        self.draw_right_panel()

    

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
        
        # Update display
        pygame.display.flip()
        
        # Control frame rate
        self.clock.tick(self.FPS)
        return True

    def cleanup(self):
        """Clean up Pygame resources"""
        pygame.quit()