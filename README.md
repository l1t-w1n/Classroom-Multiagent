# Reactive Multi-Agent System in a Classroom Environment

This project implements a multi-agent simulation modeling the interactions between teachers and children in a structured classroom environment. The simulation creates an engaging scenario where children attempt to collect candies while avoiding the teacher, who tries to maintain order by returning children to a designated safe zone.

## Project Overview

The simulation takes place in a grid-based classroom environment where two types of agents—Teacher and Child—interact within discrete sections. The environment features dynamic elements such as randomly spawning candies and a designated safe zone near the teacher's desk.

### Environment Components

#### Classroom Grid
The classroom is represented as a configurable grid (e.g., 10x10 cells) where each cell can contain:
- An agent (Teacher or Child)
- A candy
- Part of the safe zone
- Empty space

#### Safe Zone
- Located near the teacher's desk
- Serves as the initial spawn point for all agents
- Functions as a return point for captured children
- Clearly marked area in the grid

#### Candy System
- Candies spawn randomly throughout the grid
- Spawn locations exclude the safe zone
- Multiple candies can exist simultaneously
- Children can collect candies by moving onto their cell

### Agent Behaviors

#### Children (Reactive Agents)
Children employ various movement strategies to collect candies while avoiding the teacher:

1. Strategic Timing
   - Movement occurs at calculated intervals
   - Creates unpredictable patterns

2. Avoidance
   - Maintains maximum possible distance from the teacher
   - Prioritizes safety over candy collection

3. Directional Bias
   - Shows preference for specific movement directions
   - Creates predictable but potentially effective patterns

4. Random Walk
   - Chooses moves randomly from available options
   - Unpredictable movement patterns

5. Candy Seeker
   - Actively pursues the nearest candy
   - Disregards teacher proximity

Children can exist in two states:
- Free: Actively moving and collecting candies
- Captured: Being escorted back to the safe zone by the teacher

#### Teacher (Control Agent)
The teacher's primary objective is maintaining classroom order:
- Pursues and captures free children
- Escorts captured children back to the safe zone
- Uses strategic movement patterns to maximize effectiveness
- Can employ different patrol strategies
  - Target nearest child
  - Patrol high-candy-density areas
  - Follow predefined paths

### System Dynamics

#### Movement Rules
- Agents move one cell at a time
- Movement must stay within grid boundaries
- No diagonal movement allowed
- No cell can contain multiple agents

#### Candy Mechanics
- Periodic random spawning (configurable interval)
- Spawn locations exclude safe zone and occupied cells
- Instant collection upon child contact
- Disappear after collection

#### Agent Interactions
- Teacher catches child upon adjacent cell contact
- Captured children are escorted to safe zone
- Children return to free state in safe zone
- Children cannot collect candy while captured

## Technical Implementation

### Requirements
- Python 3.8+
- NumPy (for grid operations)

### Project Structure
```
project_classroom_py/
├── src/
│   ├── agents/
│   │   ├── base_agent.py
│   │   ├── child.py
│   │   └── teacher.py
│   ├── environment/
│   │   └── classroom.py
│   ├── enums.py
│   └── position.py
├── tests/
├── main.py
└── requirements.txt
```

### Setup and Running

1. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run simulation:
```bash
python main.py
```

### Configuration
The simulation offers several configurable parameters:
- Grid dimensions
- Safe zone size
- Candy spawn interval
- Agent movement speeds
- Number of agents
- Movement strategies

### Testing
Run the test suite:
```bash
python -m unittest discover tests
```

## Contributing

Feel free to contribute to this project by:
- Implementing new movement strategies
- Adding visualization improvements
- Enhancing agent behaviors
- Optimizing performance
- Adding new features

Please follow the existing code style and include appropriate tests for new features.
