import unittest
from src.position import Position

class TestPosition(unittest.TestCase):
    def test_distance_calculation(self):
        """Verify that the distance_to method correctly calculates distances."""
        pos1 = Position(0, 0)
        pos2 = Position(3, 4)
        self.assertAlmostEqual(pos1.distance_to(pos2), 5.0)

    def test_equality(self):
        """Check that the equality operator works for positions."""
        pos1 = Position(2, 3)
        pos2 = Position(2, 3)
        pos3 = Position(4, 5)
        self.assertEqual(pos1, pos2)
        self.assertNotEqual(pos1, pos3)

    def test_position_arithmetic(self):
        """Test position arithmetic for movement."""
        pos = Position(2, 2)
        
        # Test moving up
        new_pos = Position(pos.x, pos.y - 1)
        self.assertEqual(new_pos, Position(2, 1))
        
        # Test moving right
        new_pos = Position(pos.x + 1, pos.y)
        self.assertEqual(new_pos, Position(3, 2))
        
        # Test moving down
        new_pos = Position(pos.x, pos.y + 1)
        self.assertEqual(new_pos, Position(2, 3))
        
        # Test moving left
        new_pos = Position(pos.x - 1, pos.y)
        self.assertEqual(new_pos, Position(1, 2))

if __name__ == '__main__':
    unittest.main()