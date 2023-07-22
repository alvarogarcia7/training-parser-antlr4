from __future__ import annotations

import csv
import unittest
from typing import Any

from splitter import Splitter
from weight_parser.program import SingleMeasurementWeightParser, WeightParser


class Driver(unittest.TestCase):

    def test_from_file_2022(self) -> None:
        file_contents = Splitter._read_all_lines("../../data/weight_2022.txt")

        parsed = WeightParser("Mi Fit", SingleMeasurementWeightParser("2022")).parse(file_contents)

        self.assertEquals(13, len(parsed))

        self.print_as_csv("../../data/parsed_2022.csv", parsed)

    def test_from_file_2023(self) -> None:
        file_contents = Splitter._read_all_lines("../../data/weight_2023.txt")

        parsed = WeightParser("Mi Fit", SingleMeasurementWeightParser("2023")).parse(file_contents)

        self.assertEquals(7, len(parsed))

        self.print_as_csv("../../data/parsed_2023.csv", parsed)

    def print_as_csv(self, file_path_: str, parsed: list[Any]) -> None:
        with open(file_path_, mode='w+', newline='') as csvfile:
            csv_writer = csv.writer(csvfile, delimiter=';', quotechar='"')
            for row in parsed:
                row_as_columns = [row['date'],
                                  '',
                                  row['body score'],
                                  row['weight'],
                                  row['bmi'],
                                  row['body fat'],
                                  '',
                                  row['basal metabolism'],
                                  row['visceral fat'],
                                  '',
                                  row['muscle'],
                                  row['protein'],
                                  row['bone mass'],
                                  '',
                                  row['body type'],
                                  ]
                csv_writer.writerow(row_as_columns)


if __name__ == '__main__':
    unittest.main()
