from src.config.config_manager import ConfigManager
from src.position import Position
from src.enums import MovementStrategy, CellType
from src.agents.teacher import Teacher
from src.agents.child import Child
from src.environment.classroom import Classroom
from src.visualization.pygame_visualizer import ClassroomVisualizer
import random
from typing import List, Tuple, Dict

def get_grid_sections(width: int, height: int) -> Dict[str, List[Tuple[int, int]]]:
    """
    Divides the classroom grid into logical sections for strategic agent placement.
    This helps ensure agents are distributed in ways that make sense for their strategies.
    
    Args:
        width: Width of the classroom
        height: Height of the classroom
        
    Returns:
        Dictionary containing lists of positions for different areas of the classroom
    """
    sections = {
        'corners': [
            (2, 2),
            (width - 3, height - 3),
            (width - 3, 2),
            (2, height - 3)
        ],
        'edges': [
            (1, height // 4),
            (width - 2, height // 4),
            (width - 2, 3 * height // 4),
            (1, 3 * height // 4),
            (width // 4, 1),
            (3 * width // 4, 1),
            (width // 4, height - 2),
            (3 * width // 4, height - 2)
        ],
        'center_area': [
            (width // 2, height // 2),
            (width // 2 - 1, height // 2),
            (width // 2 + 1, height // 2),
            (width // 2, height // 2 - 1),
            (width // 2, height // 2 + 1)
        ],
        'mid_distance': [
            (width // 3, height // 3),
            (2 * width // 3, height // 3),
            (width // 3, 2 * height // 3),
            (2 * width // 3, 2 * height // 3)
        ],
        'safe_zone_periphery': [
            (7, 7), (8, 7), (7, 8), (8, 8),
            (6, 6), (6, 7), (7, 6)
        ],
        'candy_rich_areas': [
            (3 * width // 4, 3 * height // 4),
            (width // 4, 3 * height // 4),
            (3 * width // 4, height // 4),
            (width // 4, height // 4)
        ]
    }
    
    # Generate additional positions spread throughout the classroom
    scattered_positions = []
    for i in range(width // 3):
        for j in range(height // 3):
            x = 3 + (i * 3)
            y = 3 + (j * 3)
            if x < width - 3 and y < height - 3:
                scattered_positions.append((x, y))
    sections['scattered'] = scattered_positions
    
    return sections

def create_child_positions(config: ConfigManager) -> List[Tuple[int, int, MovementStrategy]]:
    """
    Creates a complete list of child configurations based on the settings.
    Strategically places children based on their movement strategies.
    
    Args:
        config: Configuration manager containing agent counts and classroom parameters
        
    Returns:
        List of tuples containing (x, y, strategy) for each child
    """
    width, height = config.classroom_size
    sections = get_grid_sections(width, height)
    child_configs = []
    
    # Strategy placement definitions
    strategy_placements = {
        MovementStrategy.RANDOM_WALK: {
            'positions': sections['scattered'],
            'count': config.agent_counts['num_random_walkers'],
            'description': 'Distributed throughout for maximum coverage'
        },
        MovementStrategy.CANDY_SEEKER: {
            'positions': sections['candy_rich_areas'],
            'count': config.agent_counts['num_candy_seekers'],
            'description': 'Placed in areas likely to have candies'
        },
        MovementStrategy.AVOIDANCE: {
            'positions': sections['edges'] + sections['corners'],
            'count': config.agent_counts['num_avoiders'],
            'description': 'Starting near edges for easy escape routes'
        },
        MovementStrategy.DIRECTIONAL_BIAS: {
            'positions': sections['mid_distance'],
            'count': config.agent_counts['num_directional'],
            'description': 'Placed in middle distances for movement flexibility'
        },
        MovementStrategy.STRATEGIC_TIMING: {
            'positions': sections['scattered'],
            'count': config.agent_counts['num_strategic_timers'],
            'description': 'Spread out for timing-based movements'
        },
        MovementStrategy.WALL_HUGGER: {
            'positions': sections['edges'],
            'count': config.agent_counts['num_wall_huggers'],
            'description': 'Starting near walls as per strategy'
        },
        MovementStrategy.GROUP_SEEKER: {
            'positions': sections['center_area'],
            'count': config.agent_counts['num_group_seekers'],
            'description': 'Clustered in center for group formation'
        },
        MovementStrategy.CANDY_HOARDER: {
            'positions': sections['candy_rich_areas'],
            'count': config.agent_counts['num_candy_hoarders'],
            'description': 'Near likely candy spawn points'
        },
        MovementStrategy.SAFE_EXPLORER: {
            'positions': sections['safe_zone_periphery'],
            'count': config.agent_counts['num_safe_explorers'],
            'description': 'Near safe zone for exploration'
        },
        MovementStrategy.UNPREDICTABLE: {
            'positions': sections['scattered'],
            'count': config.agent_counts['num_unpredictable'],
            'description': 'Randomly distributed'
        }
    }

    # Place children according to their strategies
    for strategy, placement in strategy_placements.items():
        positions = placement['positions'].copy()
        count = placement['count']
        
        # Shuffle positions to randomize placement while maintaining strategic positioning
        random.shuffle(positions)
        
        # Add children of this strategy type
        for i in range(min(count, len(positions))):
            x, y = positions[i]
            child_configs.append((x, y, strategy))
    
    return child_configs

def create_teacher_positions(config: ConfigManager) -> List[Tuple[int, int]]:
    """
    Creates positions for teachers based on configuration.
    For multiple teachers, distributes them strategically across the classroom.
    
    Args:
        config: Configuration manager containing teacher count and classroom parameters
        
    Returns:
        List of (x, y) positions for teachers
    """
    width, height = config.classroom_size
    num_teachers = config.agent_counts['num_teachers']
    teacher_positions = []
    
    if num_teachers == 1:
        # Single teacher in center
        teacher_positions.append((width // 2, height // 2))
    else:
        # Multiple teachers distributed in a pattern
        positions = [
            (width // 3, height // 3),
            (2 * width // 3, 2 * height // 3),
            (width // 3, 2 * height // 3),
            (2 * width // 3, height // 3)
        ]
        for i in range(min(num_teachers, len(positions))):
            teacher_positions.append(positions[i])
    
    return teacher_positions

def main():
    # Load and initialize configuration
    config = ConfigManager()
    
    # Create classroom environment
    classroom = Classroom(
        width=config.classroom_size[0],
        height=config.classroom_size[1],
        safe_zone_size=config.safe_zone_size
    )
    
    # Add teachers
    teacher_positions = create_teacher_positions(config)
    for x, y in teacher_positions:
        teacher = Teacher(Position(x, y))
        classroom.teacher = teacher  # Note: Currently supports only one teacher
        classroom.grid[y][x] = CellType.TEACHER
    
    # Add children with their strategies
    child_configs = create_child_positions(config)
    for x, y, strategy in child_configs:
        child = Child(Position(x, y), strategy)
        classroom.children.append(child)
        classroom.grid[y][x] = CellType.CHILD
    
    # Create visualization system
    visualizer = ClassroomVisualizer(classroom, cell_size=config.cell_size)
    
    # Main simulation loop
    try:
        running = True
        while running:
            classroom.update()
            running = visualizer.update(classroom)
    except KeyboardInterrupt:
        print("\nSimulation stopped by user.")
    except Exception as e:
        print(f"\nError during simulation: {str(e)}")
    finally:
        visualizer.cleanup()

if __name__ == "__main__":
    main()