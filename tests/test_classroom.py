import unittest
import time
from unittest.mock import Mock

from src.position import Position
from src.enums import CellType, AgentState, MovementStrategy
from src.agents.child import Child
from src.agents.teacher import Teacher
from src.environment.classroom import Classroom

class TestPosition(unittest.TestCase):
    """Test cases for the Position class functionality"""

    def test_position_initialization(self):
        """Test that positions are correctly initialized with given coordinates"""
        pos = Position(3, 4)
        self.assertEqual(pos.x, 3)
        self.assertEqual(pos.y, 4)

    def test_distance_calculation(self):
        """Test that distance between positions is calculated correctly"""
        pos1 = Position(0, 0)
        pos2 = Position(3, 4)
        # Testing Pythagorean triple (3,4,5)
        self.assertEqual(pos1.distance_to(pos2), 5.0)

    def test_position_equality(self):
        """Test position comparison functionality"""
        pos1 = Position(1, 2)
        pos2 = Position(1, 2)
        pos3 = Position(2, 1)

        self.assertEqual(pos1, pos2)
        self.assertNotEqual(pos1, pos3)
        self.assertNotEqual(pos1, "not a position")

class TestClassroom(unittest.TestCase):
    """Test cases for the Classroom environment"""

    def setUp(self):
        """Set up a test classroom environment before each test"""
        self.width = 10
        self.height = 10
        self.safe_zone_size = (3, 3)
        self.classroom = Classroom(
            width=self.width,
            height=self.height,
            safe_zone_size=self.safe_zone_size
        )

    def test_classroom_initialization(self):
        """Test that classroom grid is properly initialized"""
        # Check dimensions
        self.assertEqual(self.classroom.grid.shape, (self.height, self.width))
        
        # Check safe zone initialization
        for y in range(self.safe_zone_size[1]):
            for x in range(self.safe_zone_size[0]):
                self.assertEqual(self.classroom.grid[y][x], CellType.SAFE_ZONE)

    def test_candy_spawning(self):
        """Test candy spawning mechanics"""
        # Force candy spawn by setting last spawn time in past
        self.classroom.last_candy_spawn = time.time() - self.classroom.candy_spawn_interval - 1
        
        # Count initial candies
        initial_candies = sum(1 for row in self.classroom.grid 
                            for cell in row if cell == CellType.CANDY)
        
        # Trigger spawn
        self.classroom.spawn_candy()
        
        # Count candies after spawn
        new_candies = sum(1 for row in self.classroom.grid 
                         for cell in row if cell == CellType.CANDY)
        
        self.assertEqual(new_candies, initial_candies + 1)

    def test_candy_spawn_timing(self):
        """Test that candy spawning respects the time interval"""
        self.classroom.last_candy_spawn = time.time()  # Just spawned
        
        # Try to spawn immediately
        initial_candies = sum(1 for row in self.classroom.grid 
                            for cell in row if cell == CellType.CANDY)
        self.classroom.spawn_candy()
        new_candies = sum(1 for row in self.classroom.grid 
                         for cell in row if cell == CellType.CANDY)
        
        # Should not have spawned new candy
        self.assertEqual(initial_candies, new_candies)

class TestChild(unittest.TestCase):
    """Test cases for Child agent behavior"""

    def setUp(self):
        """Set up test environment for child agent tests"""
        self.classroom = Classroom(width=10, height=10, safe_zone_size=(3, 3))
        self.start_pos = Position(5, 5)

    def test_child_initialization(self):
        """Test that child agents are properly initialized"""
        child = Child(self.start_pos, MovementStrategy.RANDOM_WALK)
        self.assertEqual(child.position, self.start_pos)
        self.assertEqual(child.state, AgentState.FREE)
        self.assertEqual(child.strategy, MovementStrategy.RANDOM_WALK)

    def test_candy_seeking_behavior(self):
        """Test that candy-seeking children move toward candy"""
        # Place candy in a known position
        candy_pos = Position(8, 8)
        self.classroom.grid[candy_pos.y][candy_pos.x] = CellType.CANDY
        
        # Create candy-seeking child
        child = Child(self.start_pos, MovementStrategy.CANDY_SEEKER)
        
        # Get child's move
        new_pos = child.choose_move(self.classroom)
        
        if new_pos:  # If a move is possible
            # New position should be closer to candy than current position
            current_distance = self.start_pos.distance_to(candy_pos)
            new_distance = new_pos.distance_to(candy_pos)
            self.assertLess(new_distance, current_distance)

    def test_avoidance_behavior(self):
        """Test that children with avoidance strategy move away from teacher"""
        # Place teacher in a known position
        teacher_pos = Position(8, 8)
        self.classroom.teacher = Teacher(teacher_pos)
        self.classroom.grid[teacher_pos.y][teacher_pos.x] = CellType.TEACHER
        
        # Create avoiding child
        child = Child(self.start_pos, MovementStrategy.AVOIDANCE)
        
        # Get child's move
        new_pos = child.choose_move(self.classroom)
        
        if new_pos:  # If a move is possible
            # New position should be farther from teacher than current position
            current_distance = self.start_pos.distance_to(teacher_pos)
            new_distance = new_pos.distance_to(teacher_pos)
            self.assertGreater(new_distance, current_distance)

class TestTeacher(unittest.TestCase):
    """Test cases for Teacher agent behavior"""

    def setUp(self):
        """Set up test environment for teacher agent tests"""
        self.classroom = Classroom(width=10, height=10, safe_zone_size=(3, 3))
        self.teacher_pos = Position(5, 5)
        self.teacher = Teacher(self.teacher_pos)
        self.classroom.teacher = self.teacher

    def test_teacher_initialization(self):
        """Test that teacher agent is properly initialized"""
        self.assertEqual(self.teacher.position, self.teacher_pos)
        self.assertIsNone(self.teacher.escorting_child)

    def test_teacher_catches_adjacent_child(self):
        """Test that teacher can catch a child in an adjacent cell"""
        # Place child next to teacher
        child_pos = Position(5, 6)  # Adjacent to teacher
        child = Child(child_pos, MovementStrategy.RANDOM_WALK)
        self.classroom.children.append(child)
        self.classroom.grid[child_pos.y][child_pos.x] = CellType.CHILD
        
        # Get teacher's move
        new_pos = self.teacher.choose_move(self.classroom)
        
        # Teacher should move to child's position to catch it
        self.assertEqual(new_pos, child_pos)

    def test_teacher_escorts_to_safe_zone(self):
        """Test that teacher properly escorts caught children to safe zone"""
        # Create a captured child
        child = Child(self.teacher_pos, MovementStrategy.RANDOM_WALK)
        child.state = AgentState.CAPTURED
        self.teacher.escorting_child = child
        
        # Get teacher's move
        new_pos = self.teacher.choose_move(self.classroom)
        
        if new_pos:  # If a move is possible
            # Should be moving toward safe zone
            distance_to_safe = min(
                new_pos.distance_to(safe_pos)
                for safe_pos in self.classroom.safe_zone
            )
            current_distance = min(
                self.teacher_pos.distance_to(safe_pos)
                for safe_pos in self.classroom.safe_zone
            )
            self.assertLess(distance_to_safe, current_distance)

class TestIntegration(unittest.TestCase):
    """Integration tests for the complete simulation system"""

    def setUp(self):
        """Set up complete simulation environment"""
        self.classroom = Classroom(width=10, height=10, safe_zone_size=(3, 3))
        self.teacher = Teacher(Position(5, 5))
        self.classroom.teacher = self.teacher
        self.classroom.grid[5][5] = CellType.TEACHER

    def test_complete_simulation_step(self):
        """Test a complete simulation step with multiple agents"""
        # Add children with different strategies
        children = [
            Child(Position(1, 1), MovementStrategy.RANDOM_WALK),
            Child(Position(8, 8), MovementStrategy.CANDY_SEEKER),
            Child(Position(3, 7), MovementStrategy.AVOIDANCE)
        ]
        
        for child in children:
            self.classroom.children.append(child)
            self.classroom.grid[child.position.y][child.position.x] = CellType.CHILD

        # Record initial positions
        initial_positions = {
            agent: Position(agent.position.x, agent.position.y)
            for agent in [self.teacher] + children
        }
        
        # Run one simulation step
        self.classroom.update()
        
        # Verify all agents have valid positions
        for agent in [self.teacher] + children:
            # Position should be within grid bounds
            self.assertTrue(0 <= agent.position.x < self.classroom.width)
            self.assertTrue(0 <= agent.position.y < self.classroom.height)
            
            # If agent moved, should be to adjacent cell
            if agent.position != agent.previous_position:
                distance = agent.position.distance_to(agent.previous_position)
                self.assertAlmostEqual(distance, 1.0)

def run_tests():
    """Run all tests with detailed output"""
    unittest.main(verbosity=2)

if __name__ == '__main__':
    run_tests()
