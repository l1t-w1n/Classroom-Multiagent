import unittest
from src.environment.classroom import Classroom
from src.enums import CellType

class TestClassroom(unittest.TestCase):
    def setUp(self):
        # Initialize a test classroom with a 4x4 safe zone in the top-left corner
        self.classroom = Classroom(10, 10, (4, 4))

    def test_grid_initialization(self):
        """Test that the classroom grid initializes with the correct dimensions."""
        self.assertEqual(len(self.classroom.grid), 10)
        self.assertEqual(len(self.classroom.grid[0]), 10)

    def test_safe_zone_setup(self):
        """Verify that the safe zone is correctly initialized."""
        safe_zone_positions = [(x, y) for y in range(4) for x in range(4)]
        for pos in safe_zone_positions:
            self.assertEqual(self.classroom.grid[pos[1]][pos[0]], CellType.SAFE_ZONE)

    def test_is_position_in_safe_zone(self):
        """Check that is_position_safe_zone correctly identifies safe zone positions."""
        # Test a position inside the safe zone
        self.assertTrue(self.classroom.is_position_safe_zone(2, 2))
        # Test a position outside the safe zone
        self.assertFalse(self.classroom.is_position_safe_zone(5, 5))

    def test_candy_spawning(self):
        """Test that candies spawn at valid locations."""
        # Spawn a few candies
        for _ in range(5):
            self.classroom.spawn_candy()

        # Check that candies are in valid positions (not in the safe zone or occupied cells)
        candy_positions = [(x, y) for y in range(10) for x in range(10)
                           if self.classroom.grid[y][x] == CellType.CANDY]
        for pos in candy_positions:
            self.assertNotEqual(self.classroom.grid[pos[1]][pos[0]], CellType.SAFE_ZONE)
            self.assertNotEqual(self.classroom.grid[pos[1]][pos[0]], CellType.CHILD)
            self.assertNotEqual(self.classroom.grid[pos[1]][pos[0]], CellType.TEACHER)

    def test_candy_limit(self):
        """Ensure that the candy limit is respected."""
        # Spawn candies until the limit is reached
        while sum(1 for row in self.classroom.grid for cell in row if cell == CellType.CANDY) < 5:
            self.classroom.spawn_candy()

        # Try to spawn another candy and check that it doesn't appear
        prev_candy_count = sum(1 for row in self.classroom.grid for cell in row if cell == CellType.CANDY)
        self.classroom.spawn_candy()
        new_candy_count = sum(1 for row in self.classroom.grid for cell in row if cell == CellType.CANDY)
        self.assertEqual(prev_candy_count, new_candy_count)


if __name__ == '__main__':
    unittest.main()