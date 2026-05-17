import sys
from typing import Any

from maze_generator import MazeGenerator


def get_config(path: str) -> dict[str, Any]:
    """Read config values from a KEY=VALUE file.

    Args:
        path: Path to the config file.

    Returns:
        Dictionary with the values needed by the main program.
    """

    config: dict[str, Any] = {}
    keys = {
        "WIDTH": "width",
        "HEIGHT": "height",
        "ENTRY": "entry",
        "EXIT": "exit",
        "OUTPUT_FILE": "output_file",
        "PERFECT": "perfect",
        "SEED": "seed",
    }
    with open(path, "r", encoding="utf-8") as config_file:
        for line in config_file:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            key, value = line.split("=", 1)
            key = keys[key.strip()]
            value = value.strip()
            if key in ("width", "height", "seed"):
                config[key] = int(value)
            elif key in ("entry", "exit"):
                x, y = value.split(",", 1)
                config[key] = (int(x), int(y))
            elif key == "perfect":
                config[key] = value == "True"
            else:
                config[key] = value
    config.setdefault("seed", 42)
    return config


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
        generator = MazeGenerator(
            config["width"],
            config["height"],
            config["seed"],
        )
        generator.generate(
            config["entry"],
            config["exit"],
            config["perfect"],
        )
        write_output(
            config["output_file"],
            generator.output_text(config["entry"], config["exit"]),
        )
    except (OSError, ValueError) as error:
        print(f"Error: {error}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
