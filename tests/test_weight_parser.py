from __future__ import annotations

import csv
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from src.weight_parser import SingleMeasurementWeightParser, WeightParser, write_csv


class MyTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.fit = """Bodv score
00
Progress: +0.15kg
21/06 07:52 am
03.15 kg
Weight
Thick-set
Body type
5 items didn't reach goals
BMI BMI 17.2
(Increased
• Body fat 17.7 %
High
Water 49.5%
(Insufficient
Basal metabolism 1,809 kcal
Didn't reach goals
1 Visceral fat 12
(High
Reached 3 goals
C Muscle 33.90 kg
Good
© Protein 29.0%
(Normal)
Bone mass 3.40 kg
[Normal
Mi Fit"""

    def test_a_single_measurement(self) -> None:
        parsed = SingleMeasurementWeightParser("2023").parse(self.fit)

        expected_parsed = {
            "date": "21/06/2023",
            "body score": "00",
            "weight": "03,15",
            "body type": "Thick-set",
            "bmi": "17,2",
            "body fat": "17,7",
            "water": "49,5",
            "basal metabolism": "1809",
            "visceral fat": "12",
            "muscle": "33,90",
            "protein": "29,0",
            "bone mass": "3,40"
        }

        self.assertEqual(expected_parsed, parsed)

    def test_multiple_measurements(self) -> None:
        parsed = WeightParser("Mi Fit", SingleMeasurementWeightParser("2023")).parse(
            (self.fit + "\n" + self.fit).splitlines())

        self.assertEqual(2, len(parsed))

    def test_write_csv(self) -> None:
        parsed = SingleMeasurementWeightParser("2023").parse(self.fit)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "out.csv"
            write_csv(path, [parsed])
            with open(path, newline='') as f:
                rows = list(csv.reader(f, delimiter=';'))
        self.assertEqual(
            [["21/06/2023", "00", "03,15", "17,2", "17,7", "", "1809", "12", "", "33,90", "29,0", "3,40", "", "",
              "Thick-set"]],
            rows)

    def test_cli(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "weight.txt"
            source.write_text(self.fit + "\n" + self.fit)
            output = Path(tmp) / "weight.csv"
            result = subprocess.run(
                [sys.executable, "bin/weight_parser.py", str(source), "--year", "2023", "-o", str(output)],
                capture_output=True, text=True, env={"PYTHONPATH": "."})
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertEqual(2, len(output.read_text().splitlines()))


if __name__ == '__main__':
    unittest.main()
