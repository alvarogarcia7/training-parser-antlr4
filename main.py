from pprint import pprint

from src.data_access import DataAccess
from parser import Exercise


def parse_file(file_path: str) -> list[Exercise]:
    """Parse a training log file and return Exercise objects."""
    data_access = DataAccess()
    return data_access.parse_single_file(file_path)


def main() -> None:
    file_name: str = 'training-sample_initial.txt'
    result: list[Exercise] = parse_file(file_name)
    pprint(result)


if __name__ == "__main__":
    main()
