import random
from collections import deque


class MazeGenerator():
    """ """

    N, E, S, W = 1, 2, 4, 8
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
        self.grid = [[0xF] * width for _ in range(height)]

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
                    self.grid[y][x] -= self.N
                    self.grid[ny][nx] -= self.S
                elif nx - x == 1:
                    self.grid[y][x] -= self.E
                    self.grid[ny][nx] -= self.W
                elif ny - y == 1:
                    self.grid[y][x] -= self.S
                    self.grid[ny][nx] -= self.N
                elif nx - x == -1:
                    self.grid[y][x] -= self.W
                    self.grid[ny][nx] -= self.E
                x, y = nx, ny

        if not perfect:
            extra = (self.width * self.height) // 10
            for _ in range(extra):
                rx = random.randint(0, self.width - 2)
                ry = random.randint(0, self.height - 1)
                if self.grid[ry][rx] & self.E and self.grid[ry][rx + 1] & self.W:
                    self.grid[ry][rx] -= self.E
                    self.grid[ry][rx + 1] -= self.W

    def solve(self, entry: tuple, exit: tuple) -> list:
        """Returns the shortest path from entry to exit as a list of N/E/S/W letters."""
        queue = deque([(entry, [])])
        visited = {entry}
        while queue:
            (x, y), path = queue.popleft()
            if (x, y) == exit:
                return path
            for wall, nx, ny, letter in [
                (self.N, x,     y - 1, 'N'),
                (self.E, x + 1, y,     'E'),
                (self.S, x,     y + 1, 'S'),
                (self.W, x - 1, y,     'W'),
            ]:
                if self.grid[y][x] & wall == 0 and (nx, ny) not in visited:
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
        print(" ".join(f"{cell:X}" for cell in row))

    print()
    print("Path:", "".join(path))
