"""
Auto Driving Car Simulation
-----------------------------

This program simulates one or more autonomous cars on a rectangular field.
Cars can be added with a unique name, starting position, direction, and a command string.
The commands are:
    - L: rotate 90° left
    - R: rotate 90° right
    - F: move forward 1 grid point
If a car would leave the field, the F command is ignored.

When multiple cars are simulated, commands are executed concurrently (one command
per car per step). If two or more cars ever occupy the same grid cell during a step,
they are considered collided and will no longer process further commands.
"""

class Field:
    """Represents the simulation field."""

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height

    def is_within_bounds(self, x: int, y: int) -> bool:
        """
        Returns True if the position (x,y) is within the field.
        Note: A field with dimensions 10 x 10 has valid positions 0..9 for both x and y.
        """
        return 0 <= x < self.width and 0 <= y < self.height


class Car:
    """Represents an individual car with its initial state, commands, and dynamic state."""

    def __init__(self, name: str, x: int, y: int, direction: str, commands: str):
        self.name = name
        self.initial_x = x
        self.initial_y = y
        self.initial_direction = direction.upper()
        self.commands = commands.upper()
        self.reset()

    def reset(self):
        """Resets the car's dynamic state (position, direction, command index, collision state)."""
        self.x = self.initial_x
        self.y = self.initial_y
        self.direction = self.initial_direction
        self.command_index = 0
        self.collided = False
        # collision_info is a tuple: (list_of_other_car_names, (x, y), simulation_step)
        self.collision_info = None

    def has_next_command(self) -> bool:
        """Returns True if there is at least one command left to execute."""
        return self.command_index < len(self.commands)

    def execute_next_command(self, field: Field):
        """
        Executes the next command in the list if available and not collided.
        If the command is F and moving forward would take the car out of bounds,
        the command is ignored.
        """
        if not self.has_next_command() or self.collided:
            return

        cmd = self.commands[self.command_index]
        self.command_index += 1

        if cmd == "L":
            self.direction = self.rotate_left(self.direction)
        elif cmd == "R":
            self.direction = self.rotate_right(self.direction)
        elif cmd == "F":
            new_x, new_y = self.x, self.y
            if self.direction == "N":
                new_y += 1
            elif self.direction == "S":
                new_y -= 1
            elif self.direction == "E":
                new_x += 1
            elif self.direction == "W":
                new_x -= 1

            if field.is_within_bounds(new_x, new_y):
                self.x, self.y = new_x, new_y
        # Any invalid commands are ignored (should not happen as input is validated).

    # Static method because their functionality does not depend on any instance specific data or state
    @staticmethod
    def rotate_left(current_direction: str) -> str:
        """Returns the new direction after rotating 90° left."""
        mapping = {"N": "W", "W": "S", "S": "E", "E": "N"}
        return mapping[current_direction]

    @staticmethod
    def rotate_right(current_direction: str) -> str:
        """Returns the new direction after rotating 90° right."""
        mapping = {"N": "E", "E": "S", "S": "W", "W": "N"}
        return mapping[current_direction]


class Simulation:
    """
    Processes the simulation by executing one command per car per step (in lockstep).
    Checks for collisions after each step.
    """

    def __init__(self, field: Field, cars: list):
        self.field = field
        self.cars = cars
        self.step = 0

    def run(self) -> list:
        """
        Runs the simulation until all non-collided cars have executed all their commands.
        Returns a list of strings with the final positions or collision details.
        """
        # Reset simulation state (and each car's dynamic state)
        self.step = 0
        for car in self.cars:
            car.reset()

        # Continue while there is at least one car that can execute a command.
        while any(car.has_next_command() and not car.collided for car in self.cars):
            self.step += 1

            # Each non-collided car executes one command.
            for car in self.cars:
                if not car.collided and car.has_next_command():
                    car.execute_next_command(self.field)

            # After executing the step, check for collisions.
            self.check_collisions()

        # Generate and return the simulation results.
        results = []
        for car in self.cars:
            if car.collided:
                other_names, pos, step = car.collision_info
                results.append(
                    f"- {car.name}, collides with {', '.join(other_names)} at ({pos[0]},{pos[1]}) at step {step}"
                )
            else:
                results.append(f"- {car.name}, ({car.x},{car.y}) {car.direction}")
        return results

    def check_collisions(self):
        """
        Checks the current positions of all non-collided cars.
        If two or more occupy the same cell, they are marked as collided.
        """
        pos_map = {}
        for car in self.cars:
            if car.collided:
                continue
            pos = (car.x, car.y)
            pos_map.setdefault(pos, []).append(car)

        for pos, cars_at_pos in pos_map.items():
            if len(cars_at_pos) > 1:
                for car in cars_at_pos:
                    if not car.collided:
                        # Record the names of the other cars involved in the collision.
                        other_names = [other_car.name for other_car in cars_at_pos if other_car.name != car.name]
                        car.collided = True
                        car.collision_info = (other_names, pos, self.step)


class SimulationApp:
    """
    Handles the command line interface and user interactions.
    Prompts for field dimensions, allows adding cars, runs simulation, and then
    provides options to start over or exit.
    """

    def run(self):
        while True:
            print("Welcome to Auto Driving Car Simulation!\n")
            field = self.get_field()
            cars = []

            # Car addition loop.
            while True:
                print("\nPlease choose from the following options:")
                print("[1] Add a car to field")
                print("[2] Run simulation")
                option = input().strip()

                if option == "1":
                    car = self.get_car(cars, field)
                    if car:
                        cars.append(car)
                        self.print_cars(cars)
                elif option == "2":
                    if not cars:
                        print("No cars added. Please add at least one car before running simulation.")
                    else:
                        break
                else:
                    print("Invalid option. Please try again.")

            # Show list of cars before simulation.
            print("\nYour current list of cars are:")
            self.print_cars(cars)

            # Run the simulation.
            sim = Simulation(field, cars)
            results = sim.run()
            print("\nAfter simulation, the result is:")
            for res in results:
                print(res)

            # Post-simulation options.
            print("\nPlease choose from the following options:")
            print("[1] Start over")
            print("[2] Exit")
            post_option = input().strip()
            if post_option == "2":
                print("\nThank you for running the simulation. Goodbye!")
                break
            elif post_option != "1":
                print("Invalid option. Exiting simulation.")
                break
            print("")  # Blank line for spacing before starting over.

    def get_field(self) -> Field:
        """Prompts the user to enter valid field dimensions and returns a Field object."""
        while True:
            field_input = input("Please enter the width and height of the simulation field in x y format:\n")
            parts = field_input.strip().split()
            if len(parts) != 2:
                print("Invalid input. Please enter two integers separated by a space.\n")
                continue
            try:
                width = int(parts[0])
                height = int(parts[1])
                print(f"\nYou have created a field of {width} x {height}.")
                return Field(width, height)
            except ValueError:
                print("Invalid input. Please enter valid integers.\n")

    def get_car(self, existing_cars: list, field: Field) -> Car:
        """
        Prompts for a new car's details (name, initial position, direction, commands)
        and returns a Car object.
        """
        name = input("Please enter the name of the car:\n").strip()
        if any(car.name == name for car in existing_cars):
            print("A car with that name already exists. Please choose a unique name.")
            return None

        pos_input = input(f"Please enter initial position of car {name} in x y Direction format:\n").strip().split()
        if len(pos_input) != 3:
            print("Invalid input. Please enter two integers and a direction (N, S, E, W).")
            return None
        try:
            x = int(pos_input[0])
            y = int(pos_input[1])
        except ValueError:
            print("Invalid coordinates. Please enter two integers for x and y.")
            return None

        direction = pos_input[2].upper()
        if direction not in ("N", "S", "E", "W"):
            print("Invalid direction. Only N, S, E, or W are allowed.")
            return None

        if not field.is_within_bounds(x, y):
            print("Initial position is outside the field. Please try again.")
            return None

        commands = input(f"Please enter the commands for car {name}:\n").strip().upper()
        if any(ch not in "FLR" for ch in commands):
            print("Invalid command list. Only the characters F, L, and R are allowed.")
            return None

        return Car(name, x, y, direction, commands)

    def print_cars(self, cars: list):
        """Prints the current list of cars with their initial settings."""
        for car in cars:
            print(f"- {car.name}, ({car.initial_x},{car.initial_y}) {car.initial_direction}, {car.commands}")


def main():
    app = SimulationApp()
    app.run()


if __name__ == "__main__":
    main()