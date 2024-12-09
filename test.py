import unittest
from classroom import (
    Position, Child, Teacher, Classroom, 
    CellType, AgentState, MovementStrategy
)
import time

class TestPosition(unittest.TestCase):
    def test_distance_calculation(self):
        """Tests that Position class correctly calculates distances between points"""
        pos1 = Position(0, 0)
        pos2 = Position(3, 4)
        self.assertEqual(pos1.distance_to(pos2), 5.0)
        
    def test_position_equality(self):
        """Tests position comparison functionality"""
        pos1 = Position(1, 2)
        pos2 = Position(1, 2)
        pos3 = Position(2, 1)
        self.assertEqual(pos1.x, pos2.x)
        self.assertEqual(pos1.y, pos2.y)
        self.assertNotEqual(pos1.x, pos3.x)

class TestChild(unittest.TestCase):
    def setUp(self):
        """Set up a test environment before each test"""
        self.classroom = Classroom(width=5, height=5, safe_zone_size=(2, 2))
        self.start_pos = Position(2, 2)
        
    def test_child_initialization(self):
        """Tests that Child agents are properly initialized"""
        child = Child(self.start_pos, MovementStrategy.RANDOM_WALK)
        self.assertEqual(child.position.x, self.start_pos.x)
        self.assertEqual(child.position.y, self.start_pos.y)
        self.assertEqual(child.state, AgentState.FREE)
        
    def test_candy_seeking_behavior(self):
        """Tests that candy-seeking children move toward candy"""
        # Place a candy in the classroom
        self.classroom.grid[4][4] = CellType.CANDY
        child = Child(self.start_pos, MovementStrategy.CANDY_SEEKER)
        
        # Get the child's chosen move
        new_pos = child.choose_move(self.classroom)
        
        # Verify the move brings the child closer to the candy
        if new_pos:
            candy_pos = Position(4, 4)
            self.assertLess(
                new_pos.distance_to(candy_pos),
                self.start_pos.distance_to(candy_pos)
            )

    def test_avoidance_behavior(self):
        """Tests that children with avoidance strategy move away from teacher"""
        # Place a teacher in the classroom
        teacher_pos = Position(4, 4)
        self.classroom.teacher = Teacher(teacher_pos)
        self.classroom.grid[4][4] = CellType.TEACHER
        
        child = Child(self.start_pos, MovementStrategy.AVOIDANCE)
        new_pos = child.choose_move(self.classroom)
        
        if new_pos:
            self.assertGreater(
                new_pos.distance_to(teacher_pos),
                self.start_pos.distance_to(teacher_pos)
            )

class TestTeacher(unittest.TestCase):
    def setUp(self):
        self.classroom = Classroom(width=5, height=5, safe_zone_size=(2, 2))
        self.teacher_pos = Position(2, 2)
        self.teacher = Teacher(self.teacher_pos)
        
    def test_teacher_catches_nearby_child(self):
        """Tests that teacher can catch a child in adjacent cell"""
        child_pos = Position(2, 3)
        child = Child(child_pos, MovementStrategy.RANDOM_WALK)
        self.classroom.children.append(child)
        self.classroom.grid[3][2] = CellType.CHILD
        
        new_pos = self.teacher.choose_move(self.classroom)
        self.assertIsNotNone(new_pos)
        self.assertEqual(new_pos.x, child_pos.x)
        self.assertEqual(new_pos.y, child_pos.y)

class TestClassroom(unittest.TestCase):
    def setUp(self):
        self.classroom = Classroom(width=10, height=10, safe_zone_size=(3, 3))
        
    def test_safe_zone_initialization(self):
        """Tests that safe zone is properly initialized"""
        for y in range(3):
            for x in range(3):
                self.assertEqual(
                    self.classroom.grid[y][x],
                    CellType.SAFE_ZONE
                )
    
    def test_candy_spawning(self):
        """Tests candy spawning mechanics"""
        # Force candy spawn by setting last spawn time in the past
        self.classroom.last_candy_spawn = time.time() - 11
        initial_candy_count = sum(
            1 for row in self.classroom.grid 
            for cell in row 
            if cell == CellType.CANDY
        )
        
        self.classroom.spawn_candy()
        
        new_candy_count = sum(
            1 for row in self.classroom.grid 
            for cell in row 
            if cell == CellType.CANDY
        )
        self.assertEqual(new_candy_count, initial_candy_count + 1)

class TestSimulationIntegration(unittest.TestCase):
    def setUp(self):
        self.classroom = Classroom(width=10, height=10, safe_zone_size=(3, 3))
        self.teacher = Teacher(Position(5, 5))
        self.classroom.teacher = self.teacher
        
    def test_full_simulation_step(self):
        """Tests a complete simulation step with multiple agents"""
        # Add some children with different strategies
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
        
        # Run simulation step
        self.classroom.update()
        
        # Verify that agents have valid positions after update
        for agent in [self.teacher] + children:
            self.assertTrue(0 <= agent.position.x < self.classroom.width)
            self.assertTrue(0 <= agent.position.y < self.classroom.height)
            
            # Verify that agents either stayed in place or moved to adjacent cells
            if agent.position != agent.previous_position:
                distance = agent.position.distance_to(agent.previous_position)
                self.assertAlmostEqual(distance, 1.0)

def run_tests():
    """Runs all tests and provides detailed output"""
    # Create a test suite
    test_suite = unittest.TestSuite()
    
    # Add all test cases to the suite
    test_classes = [TestPosition, TestChild, TestTeacher, TestClassroom, TestSimulationIntegration]
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run the tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    return result

if __name__ == '__main__':
    run_tests()