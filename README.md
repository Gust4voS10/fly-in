*This project has been created as part of the 42 curriculum by gustada-.*

# Fly-In

## Description

**Fly-In** is a drone fleet pathfinding and simulation project. Given a map made
of hubs (nodes) connected by links, and a fleet of drones that must travel from
a `start_hub` to an `end_hub`, the program computes an optimal (or near-optimal)
route for every drone, then simulates and visualizes their movement turn by
turn using `pygame`.

The map format supports several features that make the pathfinding problem
non-trivial:

- **Zone types**: `normal`, `priority` (fast, preferred), `restricted` (slow,
  costs an extra turn), and `blocked` (impassable).
- **Capacity constraints**: both hubs (`max_drones`) and links
  (`max_link_capacity`) can limit how many drones may occupy or cross them at
  the same time.
- **Traffic prediction**: the pathfinder takes into account how many drones
  are already expected to use a given zone, spreading the fleet across
  alternative routes instead of funneling everyone through the same
  bottleneck.

The goal of the project is to explore graph algorithms (Dijkstra, BFS),
custom cost functions, and multi-agent scheduling with shared, capacity-limited
resources, while providing a clear and interactive visualization of the
result.

A set of hand-crafted maps (`maps/easy`, `maps/medium`, `maps/hard`,
`maps/challenger`) is provided to progressively stress-test the algorithm,
from simple linear paths up to a deliberately near-impossible "challenger"
map used as a research/stress benchmark.

## Instructions

### Requirements

- Python 3.10+ (the code relies on the `X | None` typing syntax)
- `pygame` (only external dependency, see `requirements.txt`)

### Installation

```bash
make install
```

This runs `python -m pip install -r requirements.txt`.

### Running the simulation

```bash
make run
```

This launches `main.py`, which:

1. Lists every `.txt` map found under `maps/` (plus `test.txt` at the repo
   root if present).
2. Asks you to pick a map by number.
3. Parses the map, computes a path for every drone, and opens a `pygame`
   window with the simulation.

### Debugging

```bash
make debug
```

Runs the program under `pdb`.

### Cleaning generated files

```bash
make clean
```

Removes `__pycache__`, `.mypy_cache`, and `.pytest_cache` directories.

### Linting

```bash
make lint         # flake8 + mypy (relaxed)
make lint-strict   # flake8 + mypy --strict
```

### Controls (simulation window)

| Key            | Action                                      |
|----------------|----------------------------------------------|
| `ENTER`        | Start / restart the simulation from the start |
| `R`            | Reset every drone back to its start position  |
| `V`            | Reverse direction (once every drone arrived)  |
| `→` / `←`      | Increase / decrease animation speed           |
| `+` / `-`      | Zoom in / out                                 |
| `ESC`          | Quit                                          |

## Algorithm Choices and Implementation Strategy

The project is organized into four layers, each with a single responsibility:

- **`parser/`** — reads the custom map DSL (`nb_drones`, `start_hub`,
  `end_hub`, `hub`, `connection` lines with `[key=value]` metadata) and builds
  a `Graph` made of `Zone` and `Connection` objects. All malformed input
  raises a `ParserError` with the offending line number.
- **`core/`** — plain data structures: `Graph` (zones + connections +
  adjacency list), `Zone`, `Connection`, `Drone`.
- **`algorithms/`** — the actual pathfinding:
  - **`Dijkstra`** is the main algorithm used to route each drone. Instead of
    treating every edge as cost `1`, it uses a custom weight function that
    combines three components:
    1. **Zone cost** — `priority` zones cost `0.5` (cheaper, so they are
       preferred), `restricted` zones cost `2` (discouraged but still usable
       when necessary), `blocked` zones are skipped entirely, everything
       else costs `1`.
    2. **Traffic penalty** — a `predicted_usage` map (built incrementally as
       each drone is routed) adds a penalty of `usage * 2` for zones that are
       already expected to be crowded. This makes Dijkstra naturally spread
       drones across different routes instead of all picking the exact same
       shortest path, which reduces bottlenecks before the simulation even
       starts.
    3. **Connection penalty** — narrow links (`max_link_capacity`) are
       penalized with `1 / max_link_capacity`, so low-capacity shortcuts are
       only taken when they are clearly worth it.
  - **`BFS`** is kept as a simpler, unweighted alternative for plain
    reachability/shortest-hop-count queries (useful for testing/comparison).
- **`simulation/`** — the `Scheduler` executes one discrete turn for the
  whole fleet: it computes which zones/links are currently occupied, then for
  every drone that isn't waiting, tries to advance it to the next zone in its
  precomputed path. A move only happens if:
  - the destination zone has spare capacity (`max_drones`),
  - the link between the two zones has spare capacity (`max_link_capacity`).

  Drones that cannot move simply wait for a turn and retry, which is what
  produces natural queuing behavior at bottlenecks. Entering a `restricted`
  zone forces the drone to spend one extra turn there (simulating a slower,
  careful crossing) before it can move again. The scheduler also supports a
  **reverse mode**, letting the whole fleet retrace its path back to the
  start once every drone has reached the goal.
- **`visualization/`** — a `pygame`-based renderer that turns the graph and
  the live drone positions into an animated map (see next section).

This layered design means the pathfinding algorithm, the turn-by-turn
simulation, and the rendering are fully decoupled: any of the three could be
swapped independently (e.g. replacing Dijkstra with A*, or the scheduler with
a different conflict-resolution strategy) without touching the others.

## Visual Representation Features

The simulation is rendered in real time with `pygame` and is designed to make
the algorithm's behavior easy to observe and reason about:

- **Auto-fitted map scaling**: the renderer inspects the bounding box of all
  zone coordinates and computes a scale factor so the whole map fits the
  screen, regardless of the map's size (from a 4-hub linear path to the
  25-drone "Impossible Dream" map).
- **Color-coded zones**: each hub is drawn as a colored circle using the
  `color` attribute from the map file (e.g. green for start/end hubs, red for
  danger/restricted areas), giving an immediate visual grouping of zone
  roles.
- **Zone-type icons**: `blocked`, `restricted`, and `priority` zones are
  overlaid with dedicated sign icons, so the zone's traversal rule is visible
  at a glance without reading the map file.
- **Live occupancy counters**: the number of drones currently inside each
  zone is displayed under the hub, making capacity bottlenecks visually
  obvious as they happen.
- **Smooth drone animation**: drones don't teleport between hubs — their
  visual position eases toward each new target every frame (speed
  configurable at runtime), and drones passing through a `restricted` zone
  visibly pause at the midpoint of the link to reflect the extra turn spent
  there.
- **Interactive info panel**: a side panel shows the current turn number,
  animation speed, zoom level, and the full control scheme.
- **Playback controls**: the simulation can be started, reset, sped up/slowed
  down, zoomed, and even played in reverse once every drone has reached the
  goal — useful for reviewing how the fleet routed itself through the map.

## Example Input and Expected Output

Example map (`maps/easy/02_simple_fork.txt`):

```
# Easy Level 2: Simple fork with two paths
nb_drones: 4

start_hub: start 0 0 [color=green]
hub: junction 1 0 [color=yellow max_drones=2]
hub: path_a 2 1 [color=blue]
hub: path_b 2 -1 [color=blue]
end_hub: goal 3 0 [color=red max_drones=3]

connection: start-junction [max_link_capacity=2]
connection: junction-path_a
connection: junction-path_b
connection: path_a-goal
connection: path_b-goal
```

Given this map, the program:

1. Parses 5 hubs and 5 connections, and registers 4 drones.
2. Computes a path for each drone from `start` to `goal`. Because
   `junction`'s link capacity is limited (`max_link_capacity=2`) and both
   `path_a` and `path_b` are equally cheap, Dijkstra's traffic-aware cost
   naturally distributes drones across both branches instead of stacking
   them all on one path, e.g.:

   ```
   Drone 1: start -> junction -> path_a -> goal
   Drone 2: start -> junction -> path_b -> goal
   Drone 3: start -> junction -> path_a -> goal
   Drone 4: start -> junction -> path_b -> goal
   ```

3. Opens a `pygame` window showing the graph. Pressing `ENTER` starts the
   simulation: each turn, the scheduler advances every drone one hop along
   its path (respecting `junction`'s `max_drones=2` capacity), and the
   renderer animates their movement until all four drones reach `goal`.

## Resources

Classic references used while working on this project:

- **Dijkstra's algorithm** — E. W. Dijkstra, *"A note on two problems in
  connexion with graphs"*, Numerische Mathematik, 1959. General reference:
  [Introduction to Algorithms (CLRS)](https://mitpress.mit.edu/9780262046305/introduction-to-algorithms/),
  chapter on single-source shortest paths.
- **Breadth-First Search** — standard graph traversal reference, see CLRS,
  chapter on elementary graph algorithms; also
  [Python `collections.deque` documentation](https://docs.python.org/3/library/collections.html#collections.deque)
  used for the queue implementation.
- **Multi-agent pathfinding / conflict resolution** — general background on
  scheduling multiple agents over a shared, capacity-limited graph (queueing
  and bottleneck behavior), a simplified analogue of the *Multi-Agent Path
  Finding (MAPF)* problem.
- **Pygame** — [Pygame official documentation](https://www.pygame.org/docs/),
  used for the rendering loop, event handling, image loading/scaling, and
  drawing primitives (`pygame.draw.circle`, `pygame.draw.line`).
- **Python typing** — [PEP 604](https://peps.python.org/pep-0604/) (`X | Y`
  union syntax) and the
  [`dataclasses` module documentation](https://docs.python.org/3/library/dataclasses.html)
  used for `Zone`, `Connection`, and `Drone`.

### AI Usage

AI assistance (Claude) was used during this project for:

- Reviewing and explaining error messages during debugging (e.g.
  parser edge cases and `ParserError` handling).
- Discussing design trade-offs for the Dijkstra cost function (how to
  combine zone cost, traffic penalty, and link-capacity penalty into a single
  weight).
- Drafting and refining this `README.md` file (structure and wording).

All core logic — the parser, the graph model, the Dijkstra/BFS
implementations, the turn-based scheduler, and the `pygame` renderer — was
designed and written by the author; AI was used as a support tool for
review, debugging discussions, and documentation, not to generate the
project's algorithmic logic wholesale.
