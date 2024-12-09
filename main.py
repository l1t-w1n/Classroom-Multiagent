import time
from src.position import Position
from src.enums import CellType, MovementStrategy
from src.agents.teacher import Teacher
from src.agents.child import Child
from src.environment.classroom import Classroom

def initialize_simulation(width: int, height: int, safe_zone_size: tuple) -> Classroom:
    """
    Sets up the initial classroom environment with teacher and children.
    
    Args:
        width: Width of the classroom grid
        height: Height of the classroom grid
        safe_zone_size: Tuple of (width, height) for the safe zone
        
    Returns:
        Initialized Classroom object with all agents placed
    """
    # Create classroom environment
    classroom = Classroom(width=width, height=height, safe_zone_size=safe_zone_size)
    
    # Add teacher in the middle of the classroom
    teacher = Teacher(Position(width // 2, height // 2))
    classroom.teacher = teacher
    classroom.grid[height // 2][width // 2] = CellType.TEACHER
    
    # Add children with different strategies at various positions
    child_configurations = [
        # (x, y, strategy)
        (1, 1, MovementStrategy.RANDOM_WALK),
        (width - 2, height - 2, MovementStrategy.CANDY_SEEKER),
        (width - 2, 1, MovementStrategy.AVOIDANCE),
        (1, height - 2, MovementStrategy.DIRECTIONAL_BIAS),
        (width // 3, height // 3, MovementStrategy.STRATEGIC_TIMING)
    ]
    
    for x, y, strategy in child_configurations:
        child = Child(Position(x, y), strategy)
        classroom.children.append(child)
        classroom.grid[y][x] = CellType.CHILD
        
    return classroom

def run_simulation(classroom: Classroom, num_steps: int, delay: float = 0.5):
    """
    Runs the simulation for a specified number of steps.
    
    Args:
        classroom: The initialized classroom environment
        num_steps: Number of simulation steps to run
        delay: Time delay between steps (for visualization)
    """
    print("Starting simulation...")
    print("\nInitial classroom state:")
    classroom.print_state()
    
    for step in range(num_steps):
        print(f"\nStep {step + 1}:")
        classroom.update()
        classroom.print_state()
        time.sleep(delay)

def main():
    """Main entry point for the classroom simulation"""
    # Configuration parameters
    CLASSROOM_WIDTH = 15
    CLASSROOM_HEIGHT = 15
    SAFE_ZONE_SIZE = (3, 3)
    NUM_SIMULATION_STEPS = 50
    STEP_DELAY = 0.5  # seconds
    
    try:
        # Initialize the simulation
        classroom = initialize_simulation(
            width=CLASSROOM_WIDTH,
            height=CLASSROOM_HEIGHT,
            safe_zone_size=SAFE_ZONE_SIZE
        )
        
        # Run the simulation
        run_simulation(
            classroom=classroom,
            num_steps=NUM_SIMULATION_STEPS,
            delay=STEP_DELAY
        )
        
    except KeyboardInterrupt:
        print("\nSimulation stopped by user.")
    except Exception as e:
        print(f"\nError during simulation: {str(e)}")
    finally:
        print("\nSimulation ended.")

if __name__ == "__main__":
    main()