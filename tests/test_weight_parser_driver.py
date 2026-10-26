from __future__ import annotations

import unittest
from pathlib import Path

from src.data_access import DataReader
from src.weight_parser import SingleMeasurementWeightParser, WeightParser, write_csv


@unittest.skipUnless(Path("data/workdir").exists(), "private data in data/workdir is not available")
class Driver(unittest.TestCase):

    def test_from_file_2022(self) -> None:
        file_contents = DataReader.read_lines("data/workdir/weight_2022.txt")

        parsed = WeightParser("Mi Fit", SingleMeasurementWeightParser("2022")).parse(file_contents)

        self.assertEqual(13, len(parsed))

        write_csv("data/workdir/parsed_2022.csv", parsed)

    def test_from_file_2023(self) -> None:
        file_contents = DataReader.read_lines("data/workdir/weight_2023.txt")

        parsed = WeightParser("Mi Fit", SingleMeasurementWeightParser("2023")).parse(file_contents)

        self.assertEqual(7, len(parsed))

        write_csv("data/workdir/parsed_2023.csv", parsed)


    def test_from_file_2026(self) -> None:
        file_contents = DataReader.read_lines("data/workdir/weight_2026.txt")

        parsed = WeightParser("Mi Fit", SingleMeasurementWeightParser("2026")).parse(file_contents)

        self.assertEqual(25, len(parsed))

        write_csv("data/workdir/parsed_2026.csv", parsed)


if __name__ == '__main__':
    unittest.main()
