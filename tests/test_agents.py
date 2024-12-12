import unittest
from src.agents.child import Child
from src.agents.teacher import Teacher
from src.environment.classroom import Classroom
from src.enums import MovementStrategy, CellType
from src.position import Position

class TestChild(unittest.TestCase):
    def setUp(self):
        # Create a small classroom for testing
        self.classroom = Classroom(10, 10, (2, 2))
        # Initialize a child with a random walk strategy at (0, 0)
        self.child = Child(Position(0, 0), MovementStrategy.RANDOM_WALK)

    def test_valid_moves(self):
        """Test that children only move to valid positions."""
        # Add the child to the classroom
        self.classroom.children.append(self.child)
        self.classroom.grid[0][0] = CellType.CHILD

        # Simulate a few moves and check validity
        for _ in range(5):
            new_pos = self.child.choose_move(self.classroom)
            if new_pos:
                self.assertIn(new_pos, self.child._get_valid_moves(self.classroom))
                # The new position should be empty or have a candy
                self.assertIn(self.classroom.grid[new_pos.y][new_pos.x], 
                              [CellType.EMPTY, CellType.CANDY])

    def test_candy_collection(self):
        """Verify that children collect candies when moving onto a candy cell."""
        # Place a candy in the adjacent cell
        candy_pos = Position(0, 1)
        self.classroom.grid[candy_pos.y][candy_pos.x] = CellType.CANDY

        # Move the child onto the candy
        self.child.move(candy_pos)
        self.classroom.grid[candy_pos.y][candy_pos.x] = CellType.CHILD

        # Check that the candy is collected (cell becomes empty)
        self.classroom.update()
        self.assertEqual(self.classroom.grid[candy_pos.y][candy_pos.x], CellType.CHILD)

    def test_capture_and_return(self):
        """Ensure children are captured by adjacent teachers and returned to the safe zone."""
        # Place a teacher adjacent to the child
        teacher_pos = Position(0, 1)
        teacher = Teacher(teacher_pos, (0, 10, 0, 10))
        self.classroom.teachers.append(teacher)
        self.classroom.grid[teacher_pos.y][teacher_pos.x] = CellType.TEACHER

        # Verify the child starts in a free state
        self.assertTrue(self.child.can_move())

        # Move the teacher onto the child's position
        teacher.move(self.child.position)
        self.classroom.grid[self.child.position.y][self.child.position.x] = CellType.TEACHER

        # Update the classroom and check the child's capture status
        self.classroom.update()
        self.assertFalse(self.child.can_move())

        # Check that the child is returned to a position in the safe zone
        self.assertIn(self.child.position, self.classroom.safe_zone)


class TestTeacher(unittest.TestCase):
    def setUp(self):
        # Set up a test classroom
        self.classroom = Classroom(10, 10, (2, 2))
        # Initialize a teacher at the center of the classroom with full patrol rights
        self.teacher = Teacher(Position(5, 5), (0, 10, 0, 10))

    def test_patrol_zone(self):
        """Test that teachers only move within their assigned patrol zones."""
        # Simulate a few moves and check that the teacher stays in the patrol zone
        for _ in range(5):
            new_pos = self.teacher.choose_move(self.classroom)
            if new_pos:
                self.assertGreaterEqual(new_pos.x, self.teacher.zone[0])
                self.assertLess(new_pos.x, self.teacher.zone[1])
                self.assertGreaterEqual(new_pos.y, self.teacher.zone[2])
                self.assertLess(new_pos.y, self.teacher.zone[3])

    def test_pursue_child(self):
        """Verify that teachers correctly identify and pursue the nearest child."""
        # Add a few children to the classroom
        child1 = Child(Position(3, 3), MovementStrategy.RANDOM_WALK)
        child2 = Child(Position(7, 7), MovementStrategy.RANDOM_WALK)
        self.classroom.children.extend([child1, child2])
        self.classroom.grid[3][3] = CellType.CHILD
        self.classroom.grid[7][7] = CellType.CHILD

        # Check that the teacher moves towards the nearest child
        new_pos = self.teacher.choose_move(self.classroom)
        self.assertLess(new_pos.distance_to(child1.position), 
                        self.teacher.position.distance_to(child1.position))

    def test_capture_child(self):
        """Ensure teachers capture children in adjacent cells."""
        # Add a child to the classroom in an adjacent cell
        child_pos = Position(5, 6)
        child = Child(child_pos, MovementStrategy.RANDOM_WALK)
        self.classroom.children.append(child)
        self.classroom.grid[child_pos.y][child_pos.x] = CellType.CHILD

        # Verify the child starts in a free state
        self.assertTrue(child.can_move())

        # Update the classroom and check the child's capture status
        self.classroom.update()
        self.assertFalse(child.can_move())

if __name__ == '__main__':
    unittest.main()