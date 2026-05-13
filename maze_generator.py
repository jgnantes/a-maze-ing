import random


class MazeGenerator():
    """ """

    def __init__(self, width: int, height: int, seed: int) -> None:
        """Initializes a MazeGenerator instance"""
        self.width = width
        self.height = height
        self.seed = seed
        random.seed(seed)
        self.grid = [[0] * width for _ in range(height)]

    def generate(self, perfect: bool=True) -> None:
        """Generates a maze"""
        visited: set = set()
        stack: list = []
        x: int
        y: int
        x, y = 0, 0
        visited.add((x, y))
        stack.append((x, y))
        
        while stack:
            neighbors = []
            for nx, ny in [(x, y-1), (x+1, y), (x, y+1), (x-1, y)]:
                if nx >= 0 and nx < self.width 
                and ny >= 0 and ny < self.height 
                and (nx, ny) not in visited:
                    neighbors.append((nx, ny))
            if not neighbors:
                stack.pop()
            else:
                nx, ny = random.choice(neighbors)
                visited.add((nx, ny))
                stack.append((nx, ny))
                if ny - y == -1:
                    self.grid[y][x] |= 1
                    self.grid[ny][nx] |= 4
                elif nx - x == 1:
                    self.grid[y][x] |= 2
                    self.grid[ny][nx] |= 8
                elif ny - y == 1:
                    self.grid[y][x] |= 4
                    self.grid[ny][nx] |= 1
                elif nx - x == -1:
                    self.grid[y][x] |= 8
                    self.grid[ny][nx] |= 2
                x, y = nx, ny
