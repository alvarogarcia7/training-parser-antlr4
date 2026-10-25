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
        self.assertEqual(stat.to_statistics_entry(), {"duration": "01:35:00"})

    def test_empty_entry(self) -> None:
        self.assertEqual(SessionStat().to_statistics_entry(), {})


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
