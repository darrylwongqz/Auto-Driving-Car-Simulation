"""
Test suite for the Auto Driving Car Simulation.

This suite uses a TDD approach to cover:
  - Field boundaries
  - Car rotations and forward movement (including out-of-bound checks)
  - Sequences of commands for a single car
  - Simulation with multiple cars, including collision detection
  - Cases where a car has no commands or runs out of commands
  - Error conditions for the interactive input functions in SimulationApp.
"""

import unittest
from unittest.mock import patch
import io

from auto_driving_simulation import Field, Car, Simulation, SimulationApp

# =============================
# Tests for Field and Car
# =============================
class TestField(unittest.TestCase):
    def test_within_bounds(self):
        field = Field(10, 10)
        self.assertTrue(field.is_within_bounds(0, 0))
        self.assertTrue(field.is_within_bounds(9, 9))
        self.assertFalse(field.is_within_bounds(10, 10))
        self.assertFalse(field.is_within_bounds(-1, 0))

class TestCar(unittest.TestCase):
    def setUp(self):
        self.field = Field(5, 5)

    def test_rotation_left(self):
        # Starting facing North; left rotation should result in West.
        car = Car("Test", 2, 2, "N", "L")
        car.execute_next_command(self.field)
        self.assertEqual(car.direction, "W")
    
    def test_rotation_right(self):
        # Starting facing North; right rotation should result in East.
        car = Car("Test", 2, 2, "N", "R")
        car.execute_next_command(self.field)
        self.assertEqual(car.direction, "E")

    def test_forward_within_bounds(self):
        # Facing North from (2,2) should move to (2,3)
        car = Car("Test", 2, 2, "N", "F")
        car.execute_next_command(self.field)
        self.assertEqual((car.x, car.y), (2, 3))
    
    def test_forward_out_of_bounds(self):
        # From (0,0) facing South, moving forward should be ignored.
        car = Car("Test", 0, 0, "S", "F")
        car.execute_next_command(self.field)
        self.assertEqual((car.x, car.y), (0, 0))

    def test_multiple_commands(self):
        # Test a sequence: F (forward), R (rotate right), F, L (rotate left)
        # Start at (1,1) facing North.
        # F: move to (1,2)
        # R: face East
        # F: move to (2,2)
        # L: face North
        car = Car("Test", 1, 1, "N", "FRFL")
        car.execute_next_command(self.field)  # F: (1,2)
        self.assertEqual((car.x, car.y), (1,2))
        car.execute_next_command(self.field)  # R: now facing East
        self.assertEqual(car.direction, "E")
        car.execute_next_command(self.field)  # F: (2,2)
        self.assertEqual((car.x, car.y), (2,2))
        car.execute_next_command(self.field)  # L: now facing North
        self.assertEqual(car.direction, "N")

# =============================
# Tests for Simulation
# =============================
class TestSimulation(unittest.TestCase):
    def test_single_car_simulation(self):
        """
        Scenario 1: Single Car Simulation
        Car A: starts at (1,2) facing N with commands FFRFFFFRRL.
        Expected final state: (5,4) facing S.
        """
        field = Field(10, 10)
        car_A = Car("A", 1, 2, "N", "FFRFFFFRRL")
        simulation = Simulation(field, [car_A])
        results = simulation.run()
        self.assertEqual(results, ["- A, (5,4) S"])
    
    def test_multi_car_simulation_collision(self):
        """
        Scenario 2: Multiple Cars Collision Simulation
        Car A: (1,2) N, commands FFRFFFFRRL
        Car B: (7,8) W, commands FFLFFFFFFF
        Expected collision at (5,4) on step 7.
        """
        field = Field(10, 10)
        car_A = Car("A", 1, 2, "N", "FFRFFFFRRL")
        car_B = Car("B", 7, 8, "W", "FFLFFFFFFF")
        simulation = Simulation(field, [car_A, car_B])
        results = simulation.run()
        expected_A = "- A, collides with B at (5,4) at step 7"
        expected_B = "- B, collides with A at (5,4) at step 7"
        self.assertEqual(results, [expected_A, expected_B])
    
    def test_simulation_partial_commands(self):
        """
        Test simulation when one car runs out of commands while the other continues.
        Car A: starts at (1,1) facing N, command: F (one step forward)
        Car B: starts at (2,2) facing E, commands: FF (two steps forward)
        Expected:
          - Car A ends at (1,2) facing N.
          - Car B ends at (4,2) facing E.
        """
        field = Field(5, 5)
        car_A = Car("A", 1, 1, "N", "F")
        car_B = Car("B", 2, 2, "E", "FF")
        simulation = Simulation(field, [car_A, car_B])
        results = simulation.run()
        expected_A = "- A, (1,2) N"
        expected_B = "- B, (4,2) E"
        self.assertIn(expected_A, results)
        self.assertIn(expected_B, results)
    
    def test_no_commands(self):
        """
        Test simulation when a car has no commands.
        The car should remain at its initial position.
        """
        field = Field(5, 5)
        car = Car("A", 1, 1, "N", "")
        simulation = Simulation(field, [car])
        results = simulation.run()
        self.assertEqual(results, ["- A, (1,1) N"])

# =============================
# Tests for SimulationApp Error Handling
# =============================
class TestSimulationAppErrors(unittest.TestCase):
    def setUp(self):
        self.app = SimulationApp()
        self.field = Field(10, 10)

    def test_get_field_invalid_input_then_valid(self):
        """
        Test get_field by simulating an invalid input sequence followed by a valid input.
        The first two attempts are invalid; the third is valid.
        """
        inputs = iter(["a b", "1", "10 10"])
        with patch("builtins.input", lambda _: next(inputs)):
            # Suppress printing by patching sys.stdout temporarily.
            with patch("sys.stdout", new=io.StringIO()):
                field = self.app.get_field()
        self.assertEqual(field.width, 10)
        self.assertEqual(field.height, 10)

    def test_get_car_invalid_duplicate_name(self):
        """
        Test that get_car returns None if the entered car name already exists.
        """
        existing_cars = [Car("A", 1, 2, "N", "FFRFFFFRRL")]
        # Simulate input: duplicate name "A"
        with patch("builtins.input", side_effect=["A"]):
            with patch("sys.stdout", new=io.StringIO()):
                car = self.app.get_car(existing_cars, self.field)
        self.assertIsNone(car)

    def test_get_car_invalid_position_format(self):
        """
        Test that get_car returns None if the initial position is not in the correct format.
        """
        # Provide: valid name, then a position with only two tokens.
        with patch("builtins.input", side_effect=["C", "1 2", "FFR"]):
            with patch("sys.stdout", new=io.StringIO()):
                car = self.app.get_car([], self.field)
        self.assertIsNone(car)

    def test_get_car_invalid_coordinates(self):
        """
        Test that get_car returns None if the coordinates are non-integer.
        """
        # Provide: valid name, then non-integer coordinate.
        with patch("builtins.input", side_effect=["C", "a 2 N", "FFR"]):
            with patch("sys.stdout", new=io.StringIO()):
                car = self.app.get_car([], self.field)
        self.assertIsNone(car)

    def test_get_car_invalid_direction(self):
        """
        Test that get_car returns None if an invalid direction is provided.
        """
        with patch("builtins.input", side_effect=["C", "1 2 X", "FFR"]):
            with patch("sys.stdout", new=io.StringIO()):
                car = self.app.get_car([], self.field)
        self.assertIsNone(car)

    def test_get_car_out_of_bounds(self):
        """
        Test that get_car returns None if the initial position is outside the field.
        """
        # For a field 10x10, (10, 10) is out of bounds.
        with patch("builtins.input", side_effect=["C", "10 10 N", "FFR"]):
            with patch("sys.stdout", new=io.StringIO()):
                car = self.app.get_car([], self.field)
        self.assertIsNone(car)

    def test_get_car_invalid_commands(self):
        """
        Test that get_car returns None if the command string contains invalid characters.
        """
        with patch("builtins.input", side_effect=["C", "1 2 N", "FFA"]):
            with patch("sys.stdout", new=io.StringIO()):
                car = self.app.get_car([], self.field)
        self.assertIsNone(car)

if __name__ == '__main__':
    # Running in verbose mode shows the name and status of each test.
    unittest.main(verbosity=2)