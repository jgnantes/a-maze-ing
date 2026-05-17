import random
from collections import deque


Cell = tuple[int, int]


class MazeGenerator():
    """Generate, solve, and export a cell-based maze.

    The internal grid stores open directions for each cell. Closed directions
    become visible walls when the maze is rendered or exported.
    """

    DIRECTIONS = {'N': (0, -1), 'E': (1, 0), 'S': (0, 1), 'W': (-1, 0)}
    WALL_BITS = {'N': 1, 'E': 2, 'S': 4, 'W': 8}

    pattern_42 = [
        [1, 0, 1, 0, 1, 1, 1],
        [1, 0, 1, 0, 0, 0, 1],
        [1, 1, 1, 0, 1, 1, 1],
        [0, 0, 1, 0, 1, 0, 0],
        [0, 0, 1, 0, 1, 1, 1],
    ]
    pattern_height = len(pattern_42)
    pattern_width = len(pattern_42[0])

    def __init__(self, width: int, height: int, seed: int) -> None:
        """Initialize a reproducible maze generator.

        Args:
            width: Number of cells in each row.
            height: Number of rows in the maze.
            seed: Random seed used to reproduce the same maze layout.

        Raises:
            ValueError: If width or height is not positive.
        """
        # The visual grid must have positive dimensions before any wall or
        # corridor can be represented.
        if width <= 0 or height <= 0:
            raise ValueError("Maze width and height must be positive.")

        self.width = width
        self.height = height
        self.seed = seed
        self.rng = random.Random(seed)

        # The grid will later decide which borders are drawn around each cell.
        self.grid: list[list[set[str]]] = []
        self.closed_42: set[Cell] = set()
        self._reset_grid()

    def _reset_grid(self) -> None:
        """Reset every cell to a fully closed visual state."""
        # Empty direction sets mean all walls are closed until generation opens
        # corridors between neighboring cells.
        self.grid = [
            [set() for _ in range(self.width)] for _ in range(self.height)
        ]
        self.closed_42 = set()

    def _in_bounds(self, cell: Cell) -> bool:
        """Check whether a coordinate can appear in the visible maze.

        Args:
            cell: Coordinate as an ``(x, y)`` pair.

        Returns:
            True if the coordinate is inside the rectangular maze grid.
        """
        x, y = cell
        return 0 <= x < self.width and 0 <= y < self.height

    def _validate_points(self, entry: Cell, exit: Cell) -> None:
        """Validate entry and exit cells before carving the maze.

        Args:
            entry: Cell where the solution path starts.
            exit: Cell where the solution path ends.

        Raises:
            ValueError: If the points overlap, are outside the grid, or collide
                with the closed 42 pattern.
        """
        # Distinct visible endpoints make the final highlighted path
        # meaningful.
        if entry == exit:
            raise ValueError("Entry and exit must be different.")
        # Endpoints outside the rectangle cannot be drawn or connected.
        if not self._in_bounds(entry):
            raise ValueError("Entry is outside maze bounds.")
        if not self._in_bounds(exit):
            raise ValueError("Exit is outside maze bounds.")
        # The 42 cells are visual blocks, so the path cannot start or end
        # inside the drawing.
        if entry in self.closed_42 or exit in self.closed_42:
            raise ValueError("Entry and exit cannot be inside the 42 pattern.")

    def _place_42(self, visited: set[Cell]) -> bool:
        """Reserve cells that form the visible 42 pattern.

        Args:
            visited: Set used by generation to avoid carving through cells.

        Returns:
            True if the pattern fits and was placed, otherwise False.
        """
        # The border keeps the closed 42 cells from touching the maze edge in
        # the final view, so the drawing is visible as an object inside paths.
        if (
                self.height < self.pattern_height + 2
                or self.width < self.pattern_width + 2
                ):
            return False

        # Centering turns the mathematical pattern matrix into screen/grid
        # coordinates inside the final maze rectangle.
        start_row = (self.height - self.pattern_height) // 2
        start_col = (self.width - self.pattern_width) // 2
        # Marked cells stay fully closed on screen; treating them as visited
        # forces the generated corridors to wrap around the 42 shape.
        for row in range(self.pattern_height):
            for col in range(self.pattern_width):
                if self.pattern_42[row][col] == 1:
                    visited.add((start_col + col, start_row + row))
                    self.closed_42.add((start_col + col, start_row + row))
        return True

    def _close_wall(self, x: int, y: int, nx: int, ny: int) -> None:
        """Close the passage between two neighboring cells.

        Args:
            x: X coordinate of the first cell.
            y: Y coordinate of the first cell.
            nx: X coordinate of the neighboring cell.
            ny: Y coordinate of the neighboring cell.
        """
        # The 42 pattern is meant to remain a solid visual drawing.
        if (x, y) in self.closed_42 or (nx, ny) in self.closed_42:
            return

        # Both cells must agree on the closed wall so the rendered line between
        # them is continuous instead of broken on one side.
        if ny - y == -1:
            self.grid[y][x].discard('N')
            self.grid[ny][nx].discard('S')
        elif nx - x == 1:
            self.grid[y][x].discard('E')
            self.grid[ny][nx].discard('W')
        elif ny - y == 1:
            self.grid[y][x].discard('S')
            self.grid[ny][nx].discard('N')
        elif nx - x == -1:
            self.grid[y][x].discard('W')
            self.grid[ny][nx].discard('E')

    def _open_wall(self, x: int, y: int, nx: int, ny: int) -> None:
        """Open the passage between two neighboring cells.

        Args:
            x: X coordinate of the first cell.
            y: Y coordinate of the first cell.
            nx: X coordinate of the neighboring cell.
            ny: Y coordinate of the neighboring cell.
        """
        # Both cells must agree on an opening so the visual corridor connects
        # cleanly between the two squares.
        if ny - y == -1:
            self.grid[y][x].add('N')
            self.grid[ny][nx].add('S')
        elif nx - x == 1:
            self.grid[y][x].add('E')
            self.grid[ny][nx].add('W')
        elif ny - y == 1:
            self.grid[y][x].add('S')
            self.grid[ny][nx].add('N')
        elif nx - x == -1:
            self.grid[y][x].add('W')
            self.grid[ny][nx].add('E')

    def _is_open_area(self, start_row: int, start_col: int) -> bool:
        """Check whether a 3x3 area would render as one open room.

        Args:
            start_row: Top row of the candidate 3x3 block.
            start_col: Left column of the candidate 3x3 block.

        Returns:
            True if all internal walls are open.
        """
        # If every internal east/south passage exists, the visual result is a
        # solid 3x3 room instead of narrow maze corridors.
        for row in range(start_row, start_row + 3):
            for col in range(start_col, start_col + 3):
                if col < start_col + 2 and 'E' not in self.grid[row][col]:
                    return False
                if row < start_row + 2 and 'S' not in self.grid[row][col]:
                    return False
        return True

    def _close_area_wall(self, start_row: int, start_col: int) -> bool:
        """Draw one wall inside a 3x3 open area.

        Args:
            start_row: Top row of the open 3x3 block.
            start_col: Left column of the open 3x3 block.

        Returns:
            True if a wall was closed without touching the 42 pattern.
        """
        # A vertical split draws a horizontal wall segment in the 3x3 room,
        # breaking the visual block into thinner corridors.
        for row in range(start_row, start_row + 2):
            for col in range(start_col, start_col + 3):
                if ((col, row) not in self.closed_42
                        and (col, row + 1) not in self.closed_42):
                    self._close_wall(col, row, col, row + 1)
                    return True

        # If that would touch the 42, draw a vertical wall segment instead so
        # the 3x3 room is still broken without damaging the pattern.
        for row in range(start_row, start_row + 3):
            for col in range(start_col, start_col + 2):
                if ((col, row) not in self.closed_42
                        and (col + 1, row) not in self.closed_42):
                    self._close_wall(col, row, col + 1, row)
                    return True

        return False

    def _fix_open_areas(self) -> None:
        """Remove visible 3x3 rooms from the generated maze."""
        # Keep scanning until the final maze has no visible 3x3 open rooms.
        changed = True
        while changed:
            changed = False
            # After drawing one wall, restart because overlapping 3x3 areas may
            # now look different in the final grid.
            for row in range(self.height - 2):
                for col in range(self.width - 2):
                    if self._is_open_area(row, col):
                        changed = self._close_area_wall(row, col)
                    if changed:
                        break
                if changed:
                    break

    def generate(
            self,
            entry: Cell,
            exit: Cell,
            perfect: bool = True
            ) -> None:
        """Generate a maze between entry and exit.

        Args:
            entry: Cell where the solution path starts.
            exit: Cell where the solution path ends.
            perfect: If True, keep a single route between cells. If False,
                open extra passages to create visual loops.

        Raises:
            ValueError: If the 42 pattern does not fit or the endpoints are
                invalid.
        """
        # Resetting removes old visual walls and paths before drawing a new
        # maze.
        self._reset_grid()
        visited: set[Cell] = set()

        # Marking the 42 first reserves those squares as closed visual blocks
        # before the corridor carving begins.
        if not self._place_42(visited):
            raise ValueError("Maze too small to embed the '42' pattern.")
        self._validate_points(entry, exit)

        # DFS with backtracking carves one-cell-wide corridors, which appears
        # visually as a branching maze instead of a random set of openings.
        stack: list[Cell] = []
        x, y = entry
        visited.add((x, y))
        stack.append((x, y))

        while stack:
            neighbors: list[Cell] = []

            # Candidate neighbors are adjacent grid cells that can become the
            # next visible corridor segment.
            for nx, ny in [(x, y - 1), (x + 1, y), (x, y + 1), (x - 1, y)]:
                if self._in_bounds((nx, ny)) and (nx, ny) not in visited:
                    neighbors.append((nx, ny))

            # Dead ends remain visible as corridor endings; backtracking moves
            # the carving point to a cell that may still branch.
            if not neighbors:
                stack.pop()
                if stack:
                    x, y = stack[-1]
            else:
                # A random unvisited neighbor decides where the next visible
                # corridor segment is carved.
                nx, ny = self.rng.choice(neighbors)
                visited.add((nx, ny))
                stack.append((nx, ny))
                self._open_wall(x, y, nx, ny)
                x, y = nx, ny

        if not perfect:
            # Extra openings remove some visible dead ends and create loops the
            # viewer can choose between.
            extra = (self.width * self.height) // 10
            for _ in range(extra):
                rx = self.rng.randint(0, self.width - 2)
                ry = self.rng.randint(0, self.height - 1)
                if (
                        (rx, ry) in self.closed_42
                        or (rx + 1, ry) in self.closed_42
                        ):
                    continue
                if 'E' not in self.grid[ry][rx]:
                    self.grid[ry][rx].add('E')
                    self.grid[ry][rx + 1].add('W')
        self._fix_open_areas()

    def solve(self, entry: Cell, exit: Cell) -> list[str]:
        """Find the shortest path from entry to exit.

        Args:
            entry: Cell where the path starts.
            exit: Cell where the path ends.

        Returns:
            A list of direction letters that form the shortest valid route.

        Raises:
            ValueError: If entry or exit is outside the maze bounds.
        """
        # A visual path can only be drawn between cells that exist in the grid.
        if not self._in_bounds(entry) or not self._in_bounds(exit):
            raise ValueError("Entry and exit must be inside maze bounds.")

        # BFS finds the shortest route that will be highlighted in the visual
        # display from entry to exit.
        queue: deque[tuple[Cell, list[str]]] = deque([(entry, [])])
        visited: set[Cell] = {entry}
        while queue:
            (x, y), path = queue.popleft()
            if (x, y) == exit:
                return path

            # Only open directions are valid visual moves between cells.
            for letter, (dx, dy) in self.DIRECTIONS.items():
                nx, ny = x + dx, y + dy
                if letter in self.grid[y][x] and (nx, ny) not in visited:
                    visited.add((nx, ny))
                    queue.append(((nx, ny), path + [letter]))
        return []

    def to_hex_rows(self) -> list[str]:
        """Convert the maze walls into hexadecimal rows.

        Returns:
            One string per maze row, with one hexadecimal wall digit per cell.
        """
        rows: list[str] = []
        all_walls = {'N', 'E', 'S', 'W'}

        # The hex digit records which borders the visualizer should draw around
        # each cell: N=1, E=2, S=4, W=8.
        for row in self.grid:
            values: list[str] = []
            for cell in row:
                closed_walls = all_walls - cell
                value = sum(self.WALL_BITS[wall] for wall in closed_walls)
                values.append(f"{value:X}")
            rows.append("".join(values))
        return rows

    def output_text(self, entry: Cell, exit: Cell) -> str:
        """Build the complete text expected in the output file.

        Args:
            entry: Cell where the solution path starts.
            exit: Cell where the solution path ends.

        Returns:
            Maze rows, entry, exit, and shortest path formatted as text.
        """
        # The same shortest path that can be highlighted visually is appended
        # after the wall grid for automated checking.
        path = "".join(self.solve(entry, exit))

        # Hex rows describe the visible walls; the blank line separates the map
        # from metadata about the entry, exit, and path.
        lines = self.to_hex_rows()
        lines.extend([
            "",
            f"{entry[0]},{entry[1]}",
            f"{exit[0]},{exit[1]}",
            path,
        ])
        return "\n".join(lines) + "\n"


if __name__ == "__main__":
    mg = MazeGenerator(20, 20, 42)
    entry = (0, 0)
    exit = (19, 19)
    mg.generate(entry, exit)
    path = mg.solve(entry, exit)
    print(mg.output_text(entry, exit))
