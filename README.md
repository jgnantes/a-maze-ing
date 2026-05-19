*This project has been created as part of the 42 curriculum by jnantes-, raqdos-s.*

# A-Maze-ing

## Description

A-Maze-ing is a Python maze generator and terminal visualizer. It reads a plain
text configuration file, generates a reproducible maze, writes the required
hexadecimal wall representation to an output file, and displays the maze in the
terminal.

The visual output shows walls, entry, exit, the optional shortest path, wall
colors, and the closed-cell `42` pattern required by the subject.

## Instructions

Run the project with:

```bash
python3 a_maze_ing.py config.txt
```

Using the Makefile:

```bash
make install
make run
make lint
make build
make clean
```

The default Makefile uses `.venv` as the local virtual environment.

During execution, the terminal interface accepts:

- `r`: regenerate the maze with a new seed
- `p`: show or hide the shortest path
- `c`: change wall color
- `q`: quit

## Configuration File

The configuration file uses one `KEY=VALUE` pair per line. Empty lines and lines
starting with `#` are ignored.

Mandatory keys:

```text
WIDTH=11
HEIGHT=11
ENTRY=0,0
EXIT=10,10
OUTPUT_FILE=maze.txt
PERFECT=True
```

Optional keys used by this project:

```text
SEED=42
COLOR=red
```

Key meanings:

- `WIDTH`: maze width in cells
- `HEIGHT`: maze height in cells
- `ENTRY`: entry cell as `x,y`
- `EXIT`: exit cell as `x,y`
- `OUTPUT_FILE`: file where the generated maze is written
- `PERFECT`: `True` for a maze with one route, `False` for extra passages
- `SEED`: random seed for reproducible generation
- `COLOR`: initial wall color for terminal rendering

## Output Format

The generated maze is written with one hexadecimal digit per cell. Each bit
represents a closed wall:

- bit `0`: north
- bit `1`: east
- bit `2`: south
- bit `3`: west

After the maze rows, the file contains an empty line, then:

```text
entry coordinates
exit coordinates
shortest path using N/E/S/W
```

All lines end with `\n`.

## Maze Generation Algorithm

The reusable generator is implemented in `maze_generator.py` as the
`MazeGenerator` class.

The algorithm used is depth-first search with backtracking, also known as the
recursive backtracker idea, implemented iteratively with a stack.

Generation steps:

1. Start with every cell fully closed.
2. Reserve the centered `42` pattern as closed cells.
3. Start from the entry cell.
4. Choose a random unvisited neighbor.
5. Open the shared wall between the current cell and that neighbor.
6. Move to the neighbor and repeat.
7. If there is no unvisited neighbor, backtrack with the stack.
8. If `PERFECT=False`, open extra walls to create loops.
9. Remove invalid `3x3` open areas.

## Why This Algorithm

DFS with backtracking was chosen because it is simple, deterministic with a
seed, and naturally creates a connected maze. With no extra passages, it creates
a tree structure, which gives a perfect maze: one route between connected cells.

It also fits the project well because walls can be opened incrementally while
keeping neighboring cells coherent.

## Reusable Module

The reusable part of the project is `maze_generator.py`.

Basic usage:

```python
from maze_generator import MazeGenerator

maze = MazeGenerator(width=20, height=20, seed=42)
maze.generate(entry=(0, 0), exit=(19, 19), perfect=True)

grid = maze.grid
solution = maze.solve((0, 0), (19, 19))
hex_rows = maze.to_hex_rows()
output = maze.output_text((0, 0), (19, 19))
```

Useful public data and methods:

- `grid`: internal maze structure, storing open directions for each cell
- `closed_42`: cells reserved for the closed `42` pattern
- `generate(...)`: generate the maze
- `solve(...)`: return the shortest path as `N`, `E`, `S`, `W`
- `to_hex_rows()`: return the hexadecimal wall rows
- `output_text(...)`: return the complete required output file text

The package metadata is in `pyproject.toml`. The package name is
`mazegen-pkg`, and it packages only the reusable `maze_generator.py` module.

Build it with:

```bash
make build
```

Install the wheel from the generated `dist/` directory, for example:

```bash
pip install dist/mazegen_pkg-1.0.0-py3-none-any.whl
```

## Team and Project Management

Team members:

- `jnantes-`: implemented `maze_generator.py` and `pyproject.toml` for the
  reusable package.
- `raqdos-s`: implemented `a_maze_ing.py`, terminal rendering, interactions,
  and the Makefile.

Initial planning:

- Build the reusable generator first.
- Add config parsing and required output writing.
- Add terminal rendering and interactions.
- Add packaging and project automation.

How planning evolved:

- The generator was adjusted to protect the `42` pattern, prevent invalid open
  areas, and expose reusable export methods.
- The terminal program was expanded with path toggling, regeneration, and color
  changes.

What worked well:

- Separating generation from rendering made the project easier to test and
  explain.
- The seed made maze generation reproducible.

What could be improved:

- Add automated tests for malformed config files and maze validity checks.
- Add more generation algorithms as a bonus.

Tools used:

- Python 3
- Make
- flake8
- mypy
- setuptools/build
- Git

## Resources

References:

- Python documentation: https://docs.python.org/3/
- Python packaging guide: https://packaging.python.org/
- Maze Generation — Recursive Backtracking: https://aryanab.medium.com/maze-generation-recursive-backtracking-5981bc5cc766
- A_Maze_ing Guide: https://github.com/LunnaBoo/A_Maze_ing_Guide/wiki

AI usage:

- AI was used to help review the subject requirements.
- AI was used to discuss code organization and architecture, packaging and README structure.
