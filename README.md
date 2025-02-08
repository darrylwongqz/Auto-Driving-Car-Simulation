# Auto Driving Car Simulation

## Overview

The **Auto Driving Car Simulation** is a command-line based simulation program that allows you to simulate one or more autonomous cars on a rectangular field. Each car is given a unique name, a starting position, a facing direction, and a sequence of commands. The simulation processes commands concurrently—one command per car per simulation step—and detects collisions if two or more cars occupy the same grid cell during a step. Once a collision occurs, the involved cars are marked as collided and stop processing further commands.

## How It Works

- **Field:**  
  The simulation field is defined by its width and height. For example, a 10x10 field has valid positions from `(0,0)` to `(9,9)`.

- **Car Commands:**  
  Each car accepts a string of commands where:
  - `L` rotates the car 90° to the left.
  - `R` rotates the car 90° to the right.
  - `F` moves the car forward by one grid point. If moving forward would leave the field, the command is ignored.

- **Concurrent Simulation:**  
  When multiple cars are added, the simulation executes one command per car per step. If two or more cars land on the same cell during a step, they are marked as collided, and collision details are recorded (which car collided with which, the position, and the simulation step).

- **Error Handling:**  
  The program validates user input. For example, if a car’s starting position is out of bounds or a command string contains invalid characters, an error message is printed and that input is rejected.

## Files in This Project

- `auto_driving_simulation.py`  
  Contains the main simulation code including:
  - `Field`: Represents the simulation field.
  - `Car`: Represents an individual car.
  - `Simulation`: Processes commands in lockstep and detects collisions.
  - `SimulationApp`: Provides the command-line interface for user interaction.

- `test_auto_driving_simulation.py`  
  Contains unit tests using Python’s `unittest` framework. These tests cover:
  - Field boundaries and validations.
  - Car rotations, forward movements, and command sequences.
  - Simulation behavior with single and multiple cars (including collision detection).
  - Error conditions for user inputs in the `SimulationApp`.

## Requirements

- Python 3.x

## How to Run the Simulation

1. **Open your terminal.**
2. **Navigate to the project directory** where `auto_driving_simulation.py` is located.
3. **Run the simulation** using the following command:

   ```bash
   python auto_driving_simulation.py
   ``` 
4. **Follow the on-screen prompts** to create the simulation field, add cars, and run the simulation.

## Running the Unit Tests

To run the unit tests, simply paste the following command into your terminal:

   ```bash
   python -m unittest -v test_auto_driving_simulation.py
```

This command runs all the tests in verbose mode, showing detailed output for each test case.
