from __future__ import annotations

import unittest

from weight_parser.program import SingleMeasurementWeightParser, WeightParser


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


if __name__ == '__main__':
    unittest.main()
