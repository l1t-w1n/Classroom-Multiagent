# Multi-Agent Classroom Simulation

This project implements a complex, reactive multi-agent system simulating the dynamic interactions between teachers and children in a classroom environment. The simulation models a rich scenario where children employ various strategies to move around the classroom collecting candies while teachers work to maintain order by pursuing and capturing the children.

## Features

- **Highly Configurable**: The simulation's parameters can be extensively customized through the `config.ini` file. You can easily tweak settings like grid size, agent counts, movement speeds, and more to experiment with different classroom scenarios. The `ConfigManager` class handles loading and accessing these settings, making it simple to adjust the simulation to your needs.

- **Grid-based environment**: The classroom is represented by a configurable 2D grid where each cell can be empty, contain an agent (teacher or child), hold a candy, or be part of the designated "safe zone." This grid-based structure allows for clear modeling of agent positions and movement.

- **Diverse child agent strategies**: Children are implemented as reactive agents that employ a variety of movement strategies to collect candies while avoiding capture by teachers. These strategies include:

  1. _Random Walk_: The child chooses a random direction to move in each turn, leading to an unpredictable path through the classroom.
  2. _Candy Seeker_: The child actively looks for the nearest candy and moves towards it, prioritizing candy collection over other considerations.
  3. _Teacher Avoidance_: The child tries to maintain a safe distance from all teachers, moving in a way that minimizes the risk of capture.
  4. _Directional Bias_: The child has a preferred movement direction and will prioritize moving in that direction when possible, creating a unique pattern.
  5. _Strategic Timing_: The child moves at carefully timed intervals, pausing and waiting at times, in an attempt to confuse teachers and avoid detection.
  6. _Wall Hugger_: The child stays close to the classroom walls, moving along the perimeter to avoid being surrounded by teachers.
  7. _Group Seeker_: The child tries to stay close to other children, forming protective groups to reduce the chances of being singled out by a teacher.
  8. _Candy Hoarder_: The child seeks out areas with a high density of candies and attempts to collect as many as possible in a short time.
  9. _Safe Zone Explorer_: The child alternates between exploring the classroom and returning to the safety of the safe zone, trying to balance risk and reward.
  10. _Unpredictable_: The child switches between the other strategies at random intervals, making its behavior hard to predict and counter.

  These diverse strategies create a rich, dynamic environment where children are constantly adapting and reacting to the evolving situation in the classroom.

- **Intelligent teacher agents**: Teachers are control agents tasked with maintaining order in the classroom. They actively pursue and capture children who are moving around, with the goal of minimizing disruption. Teachers employ a combination of techniques to effectively patrol the classroom:

  1. _Strategy Prioritization_: Teachers analyze the strategies being used by the children in the classroom and prioritize pursuing the children employing the most disruptive strategies first. This allows them to focus on the biggest threats to classroom order.
  2. _Area Patrolling_: Teachers are assigned specific zones within the classroom to patrol. They will focus their efforts on their assigned area, only leaving it to pursue high-priority targets identified by the strategy analysis.
  3. _Pursuit and Capture_: When a teacher identifies a child to pursue, they will navigate towards the child's position, attempting to capture the child by making contact in an adjacent cell. Captured children are immediately teleported to the safe zone.
  4. _Intelligent Movement_: Teachers use a pathfinding algorithm to efficiently navigate the classroom grid, taking the shortest unobstructed path to their target. They also try to cut off predicted child movements when pursuing.

  By combining these techniques, teachers act as intelligent agents that dynamically assess the situation and take strategic actions to maintain an orderly classroom environment in the face of children's diverse candy-seeking behaviors.

- **Candy spawning system**: Candies appear periodically at random locations throughout the classroom grid (excluding the safe zone). Children can collect these candies by moving onto the candy's cell. The candy spawning system introduces an element of randomness and incentive, driving the children's movement around the classroom.

- **Safe zone mechanic**: The classroom features a designated "safe zone," typically located in a corner of the grid. This safe zone serves as a starting point for all agents and as a respawn point for children who are captured by a teacher. Children in the safe zone cannot be captured, providing a temporary reprieve from the teachers' pursuit.

- **Realistic agent interactions**: The simulation models realistic interactions between teachers and children. When a teacher moves into a cell adjacent to a child, the child is considered "captured" and is immediately teleported back to the safe zone. Captured children are unable to move or collect candies until they return to the safe zone and "recharge," representing the time-out period in a real classroom scenario.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Installation

1. Clone the repository:

   ```
   git clone https://github.com/l1t-w1n/Classroom-Multiagent.git
   cd classroom-simulation
   ```

2. (Optional) Create a virtual environment:

   ```
   python -m venv venv
   source venv/bin/activate  # For Unix/MacOS
   .\venv\Scripts\activate   # For Windows
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

### Running the Simulation

To start the classroom simulation with the default configuration, simply run:

```
python main.py
```

The simulation will begin running in your terminal, displaying a live visualization of the classroom grid and printing relevant statistics and events. You can watch the agents move around the grid in real-time and observe the emergent behaviors arising from their interactions.

### Customizing the Simulation

The simulation's parameters can be extensively customized to experiment with different classroom setups and agent configurations. These parameters are defined in the `config.ini` file and include:

- Classroom grid dimensions (`width`, `height`)
- Safe zone size (`safe_zone_size`)
- Number of each type of child agent (`num_random_walkers`, `num_candy_seekers`, etc.)
- Number of teacher agents (`num_teachers`)
- Candy spawn interval (`candy_spawn_interval`)
- Agent movement speeds (`child_speed`, `teacher_speed`)
- And more...

To customize the simulation, open the `config.ini` file in a text editor, modify the desired parameters, and save the file. The new settings will be applied the next time you run the simulation.

Experimenting with different configurations can lead to interesting emergent behaviors and insights into how various strategies and agent counts affect the classroom dynamics.

### Running Tests

The project includes a suite of unit tests to verify the correctness of the simulation components. These tests cover the major functionalities of the agents, environment, and helper classes. To run the tests, use the following command:

```
python -m unittest discover tests
```

All tests should pass if the simulation is working correctly. If any tests fail, it may indicate a bug or regression in the codebase. Please report any issues you encounter.

## Project Structure

The project's codebase is organized into the following directory structure:

```
classroom-simulation/
│
├── src/
│   ├── agents/
│   │   ├── base_agent.py
│   │   ├── child.py
│   │   └── teacher.py
│   ├── config/
│   │   └── config_manager.py
│   ├── environment/
│   │   └── classroom.py
│   ├── enums.py
│   └── position.py
│
├── tests/
│   ├── test_agents.py
│   ├── test_classroom.py
│   └── test_position.py
│
├── config.ini
├── main.py
└── requirements.txt
```

The `src` directory contains the core components of the simulation:

- `agents/`: Defines the behavior and properties of the teacher and child agents.
- `config/`: Contains the `ConfigManager` class for loading and accessing simulation parameters from the `config.ini` file.
- `environment/`: Implements the classroom grid and handles agent interactions.
- `enums.py`: Defines enumerations for agent states, strategies, and cell types.
- `position.py`: Provides a utility class for representing 2D positions in the grid.

The `tests` directory contains the unit tests for verifying the correctness of the simulation components.

The `config.ini` file stores the simulation's configuration parameters, allowing easy customization.

The `main.py` file is the entry point of the program and orchestrates the main simulation loop.

The `requirements.txt` file lists the Python dependencies required to run the project.

## Future Enhancements

While the current simulation provides a rich and dynamic environment, there are several potential avenues for future enhancement:

1. **Visualization Improvements**: Enhance the live visualization of the classroom grid, adding colors, icons, and animations to make it more engaging and informative.

2. **Machine Learning Agents**: Introduce machine learning techniques to allow the agents (particularly the teachers) to adapt their strategies over time based on the observed behaviors of the children.

3. **Realistic Classroom Scenarios**: Implement more realistic classroom scenarios, such as children asking for help, group work dynamics, or other interactions beyond candy collection.

4. **Performance Optimization**: Optimize the simulation's performance to handle larger classroom sizes and more agents efficiently.

5. **Statistical Analysis**: Add tools for collecting and analyzing statistics about agent behaviors, strategies, and outcomes to gain deeper insights into the emergent dynamics.

6. **GUI Configuration**: Create a graphical user interface for configuring the simulation parameters, making it more accessible to non-technical users.

If you're interested in contributing to any of these enhancements or have ideas for new features, please feel free to submit a pull request or open an issue on the project's repository.

## License

This project is open-source.
