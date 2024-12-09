from src.position import Position
from src.enums import MovementStrategy, CellType
from src.agents.teacher import Teacher
from src.agents.child import Child
from src.environment.classroom import Classroom
from src.visualization.pygame_visualizer import ClassroomVisualizer

def main():
    # Create classroom environment
    CLASSROOM_WIDTH = 15
    CLASSROOM_HEIGHT = 15
    SAFE_ZONE_SIZE = (3, 3)
    
    classroom = Classroom(
        width=CLASSROOM_WIDTH,
        height=CLASSROOM_HEIGHT,
        safe_zone_size=SAFE_ZONE_SIZE
    )
    
    # Add teacher
    teacher = Teacher(Position(CLASSROOM_WIDTH // 2, CLASSROOM_HEIGHT // 2))
    classroom.teacher = teacher
    classroom.grid[CLASSROOM_HEIGHT // 2][CLASSROOM_WIDTH // 2] = CellType.TEACHER
    
    # Add children with different strategies
    child_configs = [
        (1, 1, MovementStrategy.RANDOM_WALK),
        (CLASSROOM_WIDTH - 2, CLASSROOM_HEIGHT - 2, MovementStrategy.CANDY_SEEKER),
        (CLASSROOM_WIDTH - 2, 1, MovementStrategy.AVOIDANCE),
        (1, CLASSROOM_HEIGHT - 2, MovementStrategy.DIRECTIONAL_BIAS),
        (CLASSROOM_WIDTH // 3, CLASSROOM_HEIGHT // 3, MovementStrategy.STRATEGIC_TIMING)
    ]
    
    for x, y, strategy in child_configs:
        child = Child(Position(x, y), strategy)
        classroom.children.append(child)
        classroom.grid[y][x] = CellType.CHILD
    
    # Create visualizer
    visualizer = ClassroomVisualizer(classroom)
    
    try:
        # Main simulation loop
        running = True
        while running:
            # Update simulation
            classroom.update()
            
            # Update visualization
            running = visualizer.update(classroom)
            
    except KeyboardInterrupt:
        print("\nSimulation stopped by user.")
    finally:
        visualizer.cleanup()

if __name__ == "__main__":
    main()