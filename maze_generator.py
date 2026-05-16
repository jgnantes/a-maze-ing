import random
from collections import deque


class MazeGenerator():
    """ """

    OPPOSITE = {'N': 'S', 'S': 'N', 'E': 'W', 'W': 'E'}
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
        """Initializes a MazeGenerator instance"""
        self.width = width
        self.height = height
        self.seed = seed
        random.seed(seed)
        self.grid = [[set() for _ in range(width)] for _ in range(height)]

    def _place_42(self, visited: set) -> bool:
        """Marks the '42' pattern cells as visited so DFS skips them."""
        if self.height < self.pattern_height + 2 or self.width < self.pattern_width + 2:
            return False
        start_row = (self.height - self.pattern_height) // 2
        start_col = (self.width - self.pattern_width) // 2
        for row in range(self.pattern_height):
            for col in range(self.pattern_width):
                if self.pattern_42[row][col] == 1:
                    visited.add((start_col + col, start_row + row))
        return True

    def _fix_open_areas(self) -> None:
        """Adds back a wall in any 3x3 fully open area."""
        for rs in range(self.height - 2):
            for cs in range(self.width - 2):
                fully_open = True
                for r in range(rs, rs + 3):
                    for c in range(cs, cs + 3):
                        if c + 1 <= cs + 2 and 'E' not in self.grid[r][c]:
                            fully_open = False
                        if r + 1 <= rs + 2 and 'S' not in self.grid[r][c]:
                            fully_open = False
                if fully_open:
                    self.grid[rs][cs].discard('S')
                    self.grid[rs + 1][cs].discard('N')

    def generate(
            self,
            entry: tuple,
            exit: tuple,
            perfect: bool = True
            ) -> None:
        """Generates a maze"""
        visited: set = set()
        if not self._place_42(visited):
            print("Maze too small to embed the '42' pattern.")
        stack: list = []
        x, y = entry
        visited.add((x, y))
        stack.append((x, y))

        while stack:
            neighbors = []
            for nx, ny in [(x, y-1), (x+1, y), (x, y+1), (x-1, y)]:
                if nx >= 0 and nx < self.width and ny >= 0 and ny < self.height and (nx, ny) not in visited:
                    neighbors.append((nx, ny))
            if not neighbors:
                stack.pop()
                if stack:
                    x, y = stack[-1]
            else:
                nx, ny = random.choice(neighbors)
                visited.add((nx, ny))
                stack.append((nx, ny))
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
                x, y = nx, ny

        if not perfect:
            extra = (self.width * self.height) // 10
            for _ in range(extra):
                rx = random.randint(0, self.width - 2)
                ry = random.randint(0, self.height - 1)
                if 'E' not in self.grid[ry][rx]:
                    self.grid[ry][rx].add('E')
                    self.grid[ry][rx + 1].add('W')

        self._fix_open_areas()

    def solve(self, entry: tuple, exit: tuple) -> list:
        """Returns the shortest path from entry to exit as a list of N/E/S/W letters."""
        queue = deque([(entry, [])])
        visited = {entry}
        while queue:
            (x, y), path = queue.popleft()
            if (x, y) == exit:
                return path
            for letter, (dx, dy) in self.DIRECTIONS.items():
                nx, ny = x + dx, y + dy
                if letter in self.grid[y][x] and (nx, ny) not in visited:
                    visited.add((nx, ny))
                    queue.append(((nx, ny), path + [letter]))
        return []


if __name__ == "__main__":
    mg = MazeGenerator(20, 20, 42)
    entry = (0, 0)
    exit = (19, 19)
    mg.generate(entry, exit)
    path = mg.solve(entry, exit)

    for row in mg.grid:
        print(" ".join(
            f"{sum(MazeGenerator.WALL_BITS[d] for d in {'N','E','S','W'} - cell):X}"
            for cell in row
        ))

    print()
    print("Path:", "".join(path))
