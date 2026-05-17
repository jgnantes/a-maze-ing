import sys
from typing import Any
from maze_generator import MazeGenerator


RESET = "\033[0m"
COLORS = {
    "black": "\033[30m",
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "cyan": "\033[36m",
    "white": "\033[37m",
}
WALL_COLOR_NAMES = [name for name in COLORS if name != "white"]
DEFAULT_WALL_COLOR = COLORS["cyan"]

CONFIG_KEYS = {
    "WIDTH",
    "HEIGHT",
    "ENTRY",
    "EXIT",
    "OUTPUT_FILE",
    "PERFECT",
    "SEED",
    "COLOR",
}


def get_config(path: str) -> dict[str, Any]:
    """Read config values from a KEY=VALUE file.

    Args:
        path: Path to the config file.

    Returns:
        Dictionary with the values needed by the main program.

    Raises:
        ValueError if config.txt values don't match their type hint
        KeyError if any mandatory config key is missing
    """

    config: dict[str, Any] = {}
    # Each accepted key becomes one visual or output decision: maze size,
    # endpoints, file path, generation mode, seed, or wall color.
    missing = CONFIG_KEYS - {"SEED", "COLOR", "PERFECT"}
    try:
        with open(path, "r", encoding="utf-8") as config_file:
            for line in config_file:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                key, value = line.split("=", 1)
                key = key.strip()
                if key not in CONFIG_KEYS:
                    continue
                value = value.strip()
                if key in ("WIDTH", "HEIGHT", "SEED"):
                    config[key] = int(value)
                elif key in ("ENTRY", "EXIT"):
                    x, y = value.split(",", 1)
                    config[key] = (int(x), int(y))
                elif key == "PERFECT":
                    if value not in ("True", "False"):
                        raise ValueError("PERFECT must be True or False.")
                    config[key] = value == "True"
                else:
                    config[key] = value
                if key in missing:
                    missing.remove(key)
    except ValueError:
        raise ValueError(
            "data from config.txt must be in KEY=VALUE format "
            "and VALUE must be the correct type hint for KEY")
    if len(missing) == 1:
        raise KeyError(
            f"The value {next(iter(missing))} is missing from config.txt")
    elif missing:
        raise KeyError(
            f"The mandatory values for {missing} are missing from config.txt")
    config.setdefault("SEED", 42)
    config.setdefault("COLOR", "cyan")
    config.setdefault("PERFECT", True)
    return config


def generate_maze(config: dict[str, Any]) -> MazeGenerator:
    """Create and generate a maze from config values.

    Args:
        config: Parsed configuration values.

    Returns:
        Generated MazeGenerator instance.
    """

    maze = MazeGenerator(config["WIDTH"], config["HEIGHT"], config["SEED"])
    maze.generate(config["ENTRY"], config["EXIT"], config["PERFECT"])
    return maze


def write_output(path: str, content: str) -> None:
    """Write generated maze text to disk.

    Args:
        path: Output file path.
        content: Maze text using the required hexadecimal format.

    Raises:
        OSError: If the file cannot be written.
    """

    with open(path, "w", encoding="utf-8") as output_file:
        output_file.write(content)


def render_ascii(maze: MazeGenerator, config: dict[str, Any]) -> str:
    """Render the maze as ASCII text.

    Args:
        maze: Generated MazeGenerator instance.
        config: Parsed configuration and display state.

    Returns:
        ASCII representation of the maze.
    """

    entry = config["ENTRY"]
    exit_cell = config["EXIT"]
    wall_color = str(config["WALL_COLOR"])
    path_cells: set[tuple[int, int]] = set()
    lines: list[str] = []

    def choose_color(touches_42: bool) -> str:
        return COLORS["white"] if touches_42 else wall_color

    def apply_color(text: str, touches_42: bool) -> str:
        return f"{choose_color(touches_42)}{text}{RESET}"

    # The solver gives moves; the renderer needs cells. This turns the
    # shortest path into drawable coordinates that can receive ".".
    if config["SHOW_PATH"]:
        path_cell = entry
        path_cells.add(path_cell)
        for step in maze.solve(entry, exit_cell):
            dx, dy = maze.DIRECTIONS[step]
            path_cell = (path_cell[0] + dx, path_cell[1] + dy)
            path_cells.add(path_cell)
    for y in range(maze.height):
        top = ""
        middle = ""
        # Horizontal walls come from north borders. A segment is white if it
        # touches a 42 cell above or below, making the pattern outline visible.
        for x in range(maze.width):
            cell = (x, y)
            above = (x, y - 1)
            left = (x - 1, y)
            above_left = (x - 1, y - 1)
            touches_42_wall = cell in maze.closed_42 or above in maze.closed_42
            touches_42_corner = (
                touches_42_wall
                or left in maze.closed_42
                or above_left in maze.closed_42
            )
            top += apply_color("+", touches_42_corner)
            if "N" in maze.grid[y][x]:
                top += "    "
            else:
                top += apply_color("----", touches_42_wall)

        last_top = (maze.width - 1, y)
        last_above = (maze.width - 1, y - 1)
        top += apply_color("+", last_top in maze.closed_42
                           or last_above in maze.closed_42)
        # Cell interiors show the visible markers. The 42 block wins over path
        # markers so the drawing stays readable even when the path is shown.
        for x in range(maze.width):
            cell = (x, y)
            left = (x - 1, y)
            touches_42_wall = cell in maze.closed_42 or left in maze.closed_42
            if cell in maze.closed_42:
                content = f"{COLORS['white']} 42 {RESET}"
            elif cell == entry:
                content = " E  "
            elif cell == exit_cell:
                content = " X  "
            elif cell in path_cells:
                content = " .  "
            else:
                content = "    "
            if "W" in maze.grid[y][x]:
                middle += " " + content
            else:
                middle += apply_color("|", touches_42_wall) + content

        last_middle = (maze.width - 1, y)
        if "E" in maze.grid[y][-1]:
            middle += " "
        else:
            middle += apply_color("|", last_middle in maze.closed_42)
        lines.append(top)
        lines.append(middle)
    bottom = ""
    # The bottom border finishes the visual rectangle from the last row's south
    # borders, keeping 42 corners and bottom walls white.
    for x in range(maze.width):
        cell = (x, maze.height - 1)
        left = (x - 1, maze.height - 1)
        bottom += apply_color("+", cell in maze.closed_42
                              or left in maze.closed_42)
        if "S" in maze.grid[-1][x]:
            bottom += "    "
        else:
            bottom += apply_color("----", cell in maze.closed_42)

    last_bottom = (maze.width - 1, maze.height - 1)
    bottom += apply_color("+", last_bottom in maze.closed_42)
    lines.append(bottom)
    return "\n".join(lines)


def run_terminal(maze: MazeGenerator, config: dict[str, Any]) -> None:
    """Run the terminal interaction loop.

    Args:
        maze: Maze generator already initialized from the config.
        config: Parsed configuration values.
    """

    color_name = config["COLOR"]
    if color_name not in WALL_COLOR_NAMES:
        color_name = "cyan"
    color_index = WALL_COLOR_NAMES.index(color_name)
    config["WALL_COLOR"] = COLORS[WALL_COLOR_NAMES[color_index]]
    config["SHOW_PATH"] = False
    while True:
        print(render_ascii(maze, config))
        print("[r] regenerate  [p] show/hide path  [c] change color  [q] quit")
        command = input("> ").strip().lower()
        if command == "q":
            break
        if command == "c":
            color_index = (color_index + 1) % len(WALL_COLOR_NAMES)
            config["WALL_COLOR"] = COLORS[WALL_COLOR_NAMES[color_index]]
        elif command == "p":
            config["SHOW_PATH"] = not config["SHOW_PATH"]
        elif command == "r":
            config["SEED"] += 1
            maze = generate_maze(config)
            write_output(
                config["OUTPUT_FILE"],
                maze.output_text(config["ENTRY"], config["EXIT"]),
            )


def main() -> int:
    """Run the maze generator from the command line.

    Returns:
        Process exit code. Zero means success; one means a handled error.
    """

    if len(sys.argv) != 2:
        print("Usage: python3 a_maze_ing.py config.txt")
        return 1
    try:
        config = get_config(sys.argv[1])
        maze = generate_maze(config)
        write_output(
            config["OUTPUT_FILE"],
            maze.output_text(config["ENTRY"], config["EXIT"]),
        )
        run_terminal(maze, config)
    except (OSError, ValueError, KeyError) as error:
        print(f"Error: {error}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
