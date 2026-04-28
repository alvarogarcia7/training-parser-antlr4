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
                volume = exercise.total_volume()
                # Format volume as int if it's a whole number, otherwise as float
                volume_display = int(volume) if volume == int(volume) else volume
                print(f"  {exercise.__repr__()}; subtotal: {volume_display}")
                total_volume_for_workout += volume
                total_volume += volume
            print(f"  # Stats for this session")

            print(f"  Total number of exercises: {len(workout['parsed'])}")
            # Format total volume as int if it's a whole number, otherwise as float
            total_volume_display = int(total_volume_for_workout) if total_volume_for_workout == int(total_volume_for_workout) else total_volume_for_workout
            print(f"  Total volume this workout: {total_volume_display}")

        # Format total volume as int if it's a whole number, otherwise as float
        total_volume_all = int(total_volume) if total_volume == int(total_volume) else total_volume
        print(f"Total volume for all workouts: {total_volume_all}")


def main() -> None:
    splitter = Splitter()
    exercises = splitter.main(sys.argv[1])
    splitter._debug_print(exercises)

    if len(sys.argv) >= 4 and sys.argv[2] == '--output':
        splitter._write_output(exercises, sys.argv[3])


if __name__ == "__main__":
    main()
