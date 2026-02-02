import csv
import sys
from src.data_access import DataAccess, DataSerializer, ParsedWorkoutSession


class Splitter:
    def __init__(self) -> None:
        self.data_access = DataAccess()

    def main(self, file: str) -> list[ParsedWorkoutSession]:
        """Parse a multi-session training log file."""
        return self.data_access.parse_multi_session_file(file)

    @staticmethod
    def _read_all_lines(file_path: str) -> list[str]:
        """Read all lines from a file."""
        with open(file_path, 'r') as f:
            return f.readlines()

    @staticmethod
    def _write_output(exercises: list[ParsedWorkoutSession], file_path_: str) -> None:
        """Write parsed sessions to TSV file."""
        rows = DataSerializer.to_tsv_rows(exercises)
        with open(file_path_, mode='w+', newline='') as csvfile:
            csv_writer = csv.writer(csvfile, delimiter='\t', quotechar='"')
            csv_writer.writerows(rows)

    @staticmethod
    def _debug_print(workouts: list[ParsedWorkoutSession]) -> None:
        """Print detailed stats for parsed workout sessions."""
        print("Debug printing.")
        total_volume: float = 0
        for workout in workouts:
            total_volume_for_workout: float = 0
            print(f"## {workout['date']}")
            if workout['notes']:
                print(f"  Notes: {workout['notes']}")

            for exercise in workout['parsed']:
                print(f"  {exercise.__repr__()}; subtotal: {exercise.total_volume()}")
                total_volume_for_workout += exercise.total_volume()
                total_volume += exercise.total_volume()
            print(f"  # Stats for this session")

            print(f"  Total number of exercises: {len(workout['parsed'])}")
            print(f"  Total volume this workout: {total_volume_for_workout}")

        print(f"Total volume for all workouts: {total_volume}")


def main() -> None:
    splitter = Splitter()
    exercises = splitter.main(sys.argv[1])
    splitter._debug_print(exercises)

    if len(sys.argv) >= 4 and sys.argv[2] == '--output':
        splitter._write_output(exercises, sys.argv[3])


if __name__ == "__main__":
    main()
