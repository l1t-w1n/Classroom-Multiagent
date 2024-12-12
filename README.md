# Multi-Agent Classroom Simulation

This project implements a complex, reactive multi-agent system simulating the interactions between teachers and children in a classroom environment. The simulation models a scenario where children strategically move around the classroom collecting candies while avoiding teachers who work to maintain order.

## Features

- **Grid-based environment**: The classroom is represented by a configurable 2D grid where each cell can be empty, contain an agent (teacher or child), a candy, or be part of the designated "safe zone."

- **Multiple agent types**:

  - _Children_ are reactive agents employing various movement strategies to collect candies while avoiding teachers. Strategies include strategic timing, teacher avoidance, directional bias, random walking, and active candy seeking.
  - _Teachers_ are control agents tasked with maintaining order. They pursue and capture children, returning them to the safe zone. Teachers can target the nearest child, patrol high-candy areas, or follow predefined paths.

- **Candy spawning system**: Candies appear periodically at random locations (excluding the safe zone). Children collect candies by moving onto the candy's cell.

- **Safe zone mechanic**: Located near the teacher's desk, the safe zone serves as the initial spawn point and return location for captured children. It provides a temporary reprieve from the teacher's pursuit.

- **Realistic agent interactions**: Teachers capture children by making contact in an adjacent cell. Captured children are escorted back to the safe zone and are unable to collect candies until they return to the safe zone and regain their freedom.

- **Configurable simulation parameters**: The simulation offers a wide array of adjustable settings, including grid size, candy spawn intervals, agent speeds and counts, and more. These can be tweaked in the `config.ini` file.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Installation

1. Clone the repository:

   ```
   git clone https://github.com/username/classroom-simulation.git
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

The simulation will begin running in your terminal, displaying the current state of the classroom grid and relevant statistics.

### Customizing the Simulation

Simulation parameters can be adjusted by modifying the `config.ini` file. Here you can change settings like the classroom dimensions, number and types of agents, candy spawn rates, and more. Be sure to save the file after making changes.

### Running Tests

A suite of unit tests is provided to ensure the various components of the simulation are functioning as expected. To run the tests, use:

```
python -m unittest discover tests
```

All tests should pass if the simulation is working correctly.

## Project Structure

The project is organized as follows:

```
classroom-simulation/
│
├── src/
│   ├── agents/
│   │   ├── base_agent.py
│   │   ├── child.py
│   │   └── teacher.py
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

- The `src` directory contains the main components of the simulation.

  - `agents` contains the implementation of the teacher and child agents.
  - `environment` contains the classroom grid implementation.
  - `enums.py` defines useful enumerations for agent states and cell types.
  - `position.py` provides a helpful abstraction for representing positions in the grid.

- The `tests` directory contains unit tests for the various simulation components.

- `config.ini` is the configuration file for adjusting simulation parameters.

- `main.py` is the entry point of the program and runs the main simulation loop.

- `requirements.txt` lists the Python dependencies required by the project.
