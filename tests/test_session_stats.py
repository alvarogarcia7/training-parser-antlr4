"""Tests for parsing ``# stats:`` session metadata lines."""

import unittest

from src.session_stats import (
    MAX_BPM,
    SessionStat,
    is_stats_line,
    parse_session_stats,
    parse_stats_line,
    to_statistics,
)

APPLE = "# stats: (apple watch) 500 total kcal, 402 active kcal, 50 min, 111 average bpm, 71-162 range bpm"
POLAR = "# stats: (polar) 355 kcal, 50 min, 108-140 bpm, 54% from fat"


class TestAppleWatchLine(unittest.TestCase):
    """The Apple Watch example from the task description."""

    def setUp(self) -> None:
        stat = parse_stats_line(APPLE)
        assert stat is not None
        self.stat = stat

    def test_source(self) -> None:
        self.assertEqual(self.stat.source, "apple watch")

    def test_kcal(self) -> None:
        self.assertEqual(self.stat.total_kcal, 500)
        self.assertEqual(self.stat.active_kcal, 402)

    def test_duration(self) -> None:
        self.assertEqual(self.stat.duration_min, 50)

    def test_average_bpm(self) -> None:
        # The explicit "111 average bpm" is kept, not overwritten by the range.
        self.assertEqual(self.stat.avg_bpm, 111)

    def test_range_bpm_is_min_and_max(self) -> None:
        # A labelled "71-162 range bpm" is min-max.
        self.assertEqual(self.stat.min_bpm, 71)
        self.assertEqual(self.stat.max_bpm, 162)

    def test_no_fat_percent(self) -> None:
        self.assertIsNone(self.stat.fat_percent)


class TestPolarLine(unittest.TestCase):
    """The Polar example from the task description."""

    def setUp(self) -> None:
        stat = parse_stats_line(POLAR)
        assert stat is not None
        self.stat = stat

    def test_source(self) -> None:
        self.assertEqual(self.stat.source, "polar")

    def test_bare_kcal_is_total(self) -> None:
        self.assertEqual(self.stat.total_kcal, 355)
        self.assertIsNone(self.stat.active_kcal)

    def test_duration(self) -> None:
        self.assertEqual(self.stat.duration_min, 50)

    def test_bpm_range_is_avg_max(self) -> None:
        # Polar "108-140 bpm" means average 108, max 140.
        self.assertEqual(self.stat.avg_bpm, 108)
        self.assertEqual(self.stat.max_bpm, 140)

    def test_fat_percent(self) -> None:
        self.assertEqual(self.stat.fat_percent, 54)


class TestToleranceAndValidation(unittest.TestCase):
    def test_not_a_stats_line(self) -> None:
        self.assertIsNone(parse_stats_line("# just a note"))
        self.assertIsNone(parse_stats_line("Squat: 5x5 100k"))

    def test_is_stats_line(self) -> None:
        self.assertTrue(is_stats_line(APPLE))
        self.assertTrue(is_stats_line("stats: (x) 10 min"))
        self.assertFalse(is_stats_line("# note"))

    def test_incomplete_data(self) -> None:
        stat = parse_stats_line("# stats: (polar) 50 min")
        assert stat is not None
        self.assertEqual(stat.source, "polar")
        self.assertEqual(stat.duration_min, 50)
        self.assertIsNone(stat.total_kcal)
        self.assertIsNone(stat.avg_bpm)

    def test_missing_source(self) -> None:
        stat = parse_stats_line("# stats: 300 kcal, 40 min")
        assert stat is not None
        self.assertIsNone(stat.source)
        self.assertEqual(stat.total_kcal, 300)
        self.assertEqual(stat.duration_min, 40)

    def test_unknown_fields_ignored(self) -> None:
        stat = parse_stats_line("# stats: (x) 300 kcal, 99 widgets, 40 min")
        assert stat is not None
        self.assertEqual(stat.total_kcal, 300)
        self.assertEqual(stat.duration_min, 40)

    def test_bpm_cap_discards_implausible_values(self) -> None:
        stat = parse_stats_line("# stats: (x) 300 average bpm")
        assert stat is not None
        self.assertIsNone(stat.avg_bpm)

    def test_bpm_cap_keeps_avg_drops_max(self) -> None:
        stat = parse_stats_line("# stats: (x) 150-999 bpm")
        assert stat is not None
        self.assertEqual(stat.avg_bpm, 150)
        self.assertIsNone(stat.max_bpm)

    def test_boundary_bpm_allowed(self) -> None:
        stat = parse_stats_line(f"# stats: (x) {MAX_BPM} average bpm")
        assert stat is not None
        self.assertEqual(stat.avg_bpm, MAX_BPM)

    def test_zone_minutes(self) -> None:
        stat = parse_stats_line("# stats: (polar) 22 zm, 45 min")
        assert stat is not None
        self.assertEqual(stat.zone_minutes, 22)
        self.assertEqual(stat.duration_min, 45)


class TestExpandedFormats(unittest.TestCase):
    """Real-world notation variants from the TP-17 implementation notes."""

    def test_no_colon_and_bare_hash(self) -> None:
        self.assertTrue(is_stats_line("# Stats 35 min, 58 zone min, 138-164 bpm, 421 kcal"))
        self.assertTrue(is_stats_line("#Stats: 35 min"))
        stat = parse_stats_line("# Stats 35 min, 58 zone min, 138-164 bpm, 421 kcal")
        assert stat is not None
        self.assertEqual(stat.duration_min, 35)
        self.assertEqual(stat.zone_minutes, 58)
        self.assertEqual((stat.avg_bpm, stat.max_bpm), (138, 164))
        self.assertEqual(stat.total_kcal, 421)

    def test_minutes_m_suffix(self) -> None:
        stat = parse_stats_line("# Stats: 59m, 22 zm, 104-146 bpm, 360kcal")
        assert stat is not None
        self.assertEqual(stat.duration_min, 59)
        self.assertEqual(stat.zone_minutes, 22)
        self.assertEqual(stat.total_kcal, 360)  # "360kcal", no space

    def test_zm_attached_to_number(self) -> None:
        stat = parse_stats_line("# Stats: 96m, 66zm, 116-163bpm, 813 kcal")
        assert stat is not None
        self.assertEqual(stat.zone_minutes, 66)  # "66zm"
        self.assertEqual((stat.avg_bpm, stat.max_bpm), (116, 163))  # "116-163bpm"

    def test_cardio_load(self) -> None:
        stat = parse_stats_line(
            "# stats: (polar rosa) 56 min, 98-138 bpm, cardio load 24, 310 kcal, 60% fat"
        )
        assert stat is not None
        self.assertEqual(stat.source, "polar rosa")
        self.assertEqual(stat.cardio_load, 24)
        self.assertEqual(stat.fat_percent, 60)

    def test_activity_percent_is_not_fat(self) -> None:
        # "56% actividad" is activity %, not fat — must not populate fat_percent.
        stat = parse_stats_line(
            "# Stats: 32 min actividad, 104-153 bpm, 714 kcal, 56% actividad"
        )
        assert stat is not None
        self.assertIsNone(stat.fat_percent)
        self.assertEqual(stat.duration_min, 32)
        self.assertEqual(stat.total_kcal, 714)

    def test_out_of_range_bpm_typo_does_not_clobber(self) -> None:
        # "746 bpm" is a typo (> 220) and must not wipe the real range values.
        stat = parse_stats_line("# Stats: 74m, 88zm, 126-161 bpm, 746 bpm")
        assert stat is not None
        self.assertEqual((stat.avg_bpm, stat.max_bpm), (126, 161))

    def test_zone_only_line(self) -> None:
        stat = parse_stats_line("# Stats: 44 zone minutes")
        assert stat is not None
        self.assertEqual(stat.zone_minutes, 44)
        self.assertTrue(stat.has_data())

    def test_empty_stats_line_has_no_data(self) -> None:
        stat = parse_stats_line("# Stats:")
        assert stat is not None
        self.assertFalse(stat.has_data())


class TestMultipleStats(unittest.TestCase):
    def test_parse_multiple_lines_from_text(self) -> None:
        text = f"{APPLE}\nSquat: 5x5 100k\n{POLAR}\n"
        stats = parse_session_stats(text)
        self.assertEqual(len(stats), 2)
        self.assertEqual(stats[0].source, "apple watch")
        self.assertEqual(stats[1].source, "polar")

    def test_parse_from_list_of_lines(self) -> None:
        stats = parse_session_stats([APPLE, "# plain note", POLAR])
        self.assertEqual([s.source for s in stats], ["apple watch", "polar"])


# Every example line from the TP-17 task (its Description and Implementation
# Notes), paired with the exact dict parse_stats_line(...).to_dict() must yield.
# Notes on the trickier cases:
#   - apple watch: explicit "N average bpm" is the average; "a-b range bpm" is min-max.
#   - polar: a bare "a-b bpm" is average-max.
#   - carga basal / tiempo / "56% actividad" are undefined metrics and dropped
#     (activity % is not fat %); the first time value wins over a later one.
#   - "746 bpm" / "350 bpm" are typos (> 220 bpm) and are discarded without
#     clobbering the real range on the same line.
#   - the free-text Spanish note still yields its "10 minutos".
TASK_EXAMPLES: list[tuple[str, dict[str, object]]] = [
    (
        "# stats: (apple watch) 500 total kcal, 402 active kcal, 50 min, 111 average bpm, 71-162 range bpm",
        {"source": "apple watch", "total_kcal": 500, "active_kcal": 402,
         "duration_min": 50, "avg_bpm": 111, "min_bpm": 71, "max_bpm": 162},
    ),
    (
        "# stats: (polar) 355 kcal, 50 min, 108-140 bpm, 54% from fat",
        {"source": "polar", "total_kcal": 355, "duration_min": 50,
         "avg_bpm": 108, "max_bpm": 140, "fat_percent": 54},
    ),
    (
        "# Stats: 43 min, 37 zone min, 120-153 bpm, 382 kcal",
        {"total_kcal": 382, "duration_min": 43, "avg_bpm": 120,
         "max_bpm": 153, "zone_minutes": 37},
    ),
    (
        "# stats: (apple watch) 416 total kcal, 308 active kcal, 55 min, 95 average bpm, 66-145 range bpm",
        {"source": "apple watch", "total_kcal": 416, "active_kcal": 308,
         "duration_min": 55, "avg_bpm": 95, "min_bpm": 66, "max_bpm": 145},
    ),
    (
        "# stats: (polar rosa) 56 min, 98-138 bpm, cardio load 24, 310 kcal, 60% fat",
        {"source": "polar rosa", "total_kcal": 310, "duration_min": 56,
         "avg_bpm": 98, "max_bpm": 138, "fat_percent": 60, "cardio_load": 24},
    ),
    (
        "# stats: (apple watch) 353 total kcal, 265 active kcal, 45 min, 101 average bpm, 75-134 range bpm",
        {"source": "apple watch", "total_kcal": 353, "active_kcal": 265,
         "duration_min": 45, "avg_bpm": 101, "min_bpm": 75, "max_bpm": 134},
    ),
    (
        "# stats: (polar rosa) 45 min, 96-125 bpm, cardio load 17, 228 kcal, 64% fat",
        {"source": "polar rosa", "total_kcal": 228, "duration_min": 45,
         "avg_bpm": 96, "max_bpm": 125, "fat_percent": 64, "cardio_load": 17},
    ),
    (
        "# Stats: 66 min, 66 zone min, 122-146 bpm, 607 kcal",
        {"total_kcal": 607, "duration_min": 66, "avg_bpm": 122,
         "max_bpm": 146, "zone_minutes": 66},
    ),
    (
        "# Stats: 81m, 68 min zone, 120-164 bpm, 716 kcal",
        {"total_kcal": 716, "duration_min": 81, "avg_bpm": 120,
         "max_bpm": 164, "zone_minutes": 68},
    ),
    (
        "# Stats 35 min, 58 zone min, 138-164 bpm, 421 kcal",
        {"total_kcal": 421, "duration_min": 35, "avg_bpm": 138,
         "max_bpm": 164, "zone_minutes": 58},
    ),
    (
        "# Stats: 75 min, 60 zone minutes, 118-155 bpm, 617 kcal",
        {"total_kcal": 617, "duration_min": 75, "avg_bpm": 118,
         "max_bpm": 155, "zone_minutes": 60},
    ),
    (
        "# Stats: 32 min actividad, 104-153 bpm, 60 carga basal, tiempo: 1h 50m, 714 kcal, 56% actividad",
        {"total_kcal": 714, "duration_min": 32, "avg_bpm": 104, "max_bpm": 153},
    ),
    (
        "# Stats: 59m, 22 zm, 104-146 bpm, 360kcal",
        {"total_kcal": 360, "duration_min": 59, "avg_bpm": 104,
         "max_bpm": 146, "zone_minutes": 22},
    ),
    (
        "# Stats: 96m, 66zm, 116-163bpm, 813 kcal",
        {"total_kcal": 813, "duration_min": 96, "avg_bpm": 116,
         "max_bpm": 163, "zone_minutes": 66},
    ),
    (
        "# Stats: 33m, 21 zm, 116-144 bpm, 254 kcal",
        {"total_kcal": 254, "duration_min": 33, "avg_bpm": 116,
         "max_bpm": 144, "zone_minutes": 21},
    ),
    (
        "#Stats: 35 min, 28 zm, 121-154 bpm, 318 kcal",
        {"total_kcal": 318, "duration_min": 35, "avg_bpm": 121,
         "max_bpm": 154, "zone_minutes": 28},
    ),
    (
        "# Stats: 74m, 88zm, 126-161 bpm, 746 bpm",
        {"duration_min": 74, "avg_bpm": 126, "max_bpm": 161, "zone_minutes": 88},
    ),
    (
        "# Stats: 40m, 34zm, 114-139 bpm, 350 bpm",
        {"duration_min": 40, "avg_bpm": 114, "max_bpm": 139, "zone_minutes": 34},
    ),
    (
        "# Stats: 44 zone minutes",
        {"zone_minutes": 44},
    ),
    (
        "# Stats: 61 zone minutes",
        {"zone_minutes": 61},
    ),
    (
        "# Stats up to here: 44 min, 10 zone min, 100-130 bpm, 212 kcal",
        {"total_kcal": 212, "duration_min": 44, "avg_bpm": 100,
         "max_bpm": 130, "zone_minutes": 10},
    ),
    (
        "# Stats: 51 min, 32 zone minutes, 114-142 bpm, 391 kcal",
        {"total_kcal": 391, "duration_min": 51, "avg_bpm": 114,
         "max_bpm": 142, "zone_minutes": 32},
    ),
    (
        "# Stats: 22:49 de la noche. Pocas ganas. apenas 10 minutos porque hace mucho calor",
        {"duration_min": 10},
    ),
    (
        "# Stats: 117m, 124 zone minutes, 124-162 bpm, 1105 kcal",
        {"total_kcal": 1105, "duration_min": 117, "avg_bpm": 124,
         "max_bpm": 162, "zone_minutes": 124},
    ),
]


class TestTaskExamples(unittest.TestCase):
    """Every example line from the TP-17 task parses to its expected values."""

    def test_all_examples(self) -> None:
        for line, expected in TASK_EXAMPLES:
            with self.subTest(line=line):
                stat = parse_stats_line(line)
                assert stat is not None
                self.assertEqual(stat.to_dict(), expected)

    def test_all_examples_are_recognised_as_stats_lines(self) -> None:
        for line, _ in TASK_EXAMPLES:
            with self.subTest(line=line):
                self.assertTrue(is_stats_line(line))

    def test_all_examples_serialise_against_schema_entry(self) -> None:
        # Every example must produce a statsEntry the serializer accepts.
        from src.parser.serializer import serialize_to_set_centric
        from src.parser.model import Exercise, Set_, Weight

        stats = [parse_stats_line(line) for line, _ in TASK_EXAMPLES]
        result = serialize_to_set_centric(
            [Exercise("Squat", [Set_(5, Weight(100.0, "kg"))])],
            None,
            [s for s in stats if s is not None],
        )
        self.assertEqual(len(result["statistics"]["entries"]), len(TASK_EXAMPLES))


class TestToDict(unittest.TestCase):
    def test_omits_unset_fields(self) -> None:
        stat = SessionStat(source="polar", total_kcal=355, duration_min=50)
        self.assertEqual(
            stat.to_dict(),
            {"source": "polar", "total_kcal": 355, "duration_min": 50},
        )

    def test_apple_watch_full(self) -> None:
        stat = parse_stats_line(APPLE)
        assert stat is not None
        self.assertEqual(
            stat.to_dict(),
            {
                "source": "apple watch",
                "total_kcal": 500,
                "active_kcal": 402,
                "duration_min": 50,
                "avg_bpm": 111,
                "min_bpm": 71,
                "max_bpm": 162,
            },
        )


class TestStatisticsEntry(unittest.TestCase):
    """Conversion to the schema's ``statsEntry`` shape."""

    def test_apple_watch_entry(self) -> None:
        stat = parse_stats_line(APPLE)
        assert stat is not None
        self.assertEqual(
            stat.to_statistics_entry(),
            {
                "source": "apple watch",
                "duration": "00:50:00",
                "bpm": {"average": 111, "min": 71, "max": 162},
                "kcal": {"total": 500, "active": 402},
            },
        )

    def test_polar_entry(self) -> None:
        stat = parse_stats_line(POLAR)
        assert stat is not None
        self.assertEqual(
            stat.to_statistics_entry(),
            {
                "source": "polar",
                "duration": "00:50:00",
                "bpm": {"average": 108, "max": 140},
                "kcal": {"total": 355},
                "fat_percent": 54,
            },
        )

    def test_duration_over_an_hour(self) -> None:
        stat = SessionStat(duration_min=95)
        self.assertEqual(
            stat.to_statistics_entry(),
            {"source": "unknown", "duration": "01:35:00"},
        )

    def test_empty_entry_still_has_source(self) -> None:
        # source is always present; a line with no device becomes "unknown".
        self.assertEqual(SessionStat().to_statistics_entry(), {"source": "unknown"})

    def test_sourceless_line_gets_unknown(self) -> None:
        stat = parse_stats_line("# Stats: 43 min, 120-153 bpm, 382 kcal")
        assert stat is not None
        self.assertEqual(stat.to_statistics_entry()["source"], "unknown")


class TestToStatistics(unittest.TestCase):
    """Building the workout ``statistics`` object."""

    def test_empty_is_empty_object(self) -> None:
        self.assertEqual(to_statistics([]), {})

    def test_multiple_entries(self) -> None:
        stats = parse_session_stats([APPLE, POLAR])
        result = to_statistics(stats)
        self.assertEqual(len(result["entries"]), 2)
        self.assertEqual(result["entries"][0]["source"], "apple watch")
        self.assertEqual(result["entries"][1]["source"], "polar")


if __name__ == "__main__":
    unittest.main()
