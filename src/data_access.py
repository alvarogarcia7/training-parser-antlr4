"""
Data access library for reading, parsing, and updating training exercise data.

This library provides a unified interface for:
- Reading training log files
- Parsing exercise data using ANTLR4
- Standardizing exercise names
- Serializing to different JSON formats
"""

import re
from pathlib import Path
from typing import Any, Optional, TextIO, TypedDict, List

from antlr4 import CommonTokenStream, InputStream

from dist.trainingLexer import trainingLexer
from dist.trainingParser import trainingParser
from parser import Exercise, StandardizeName, Formatter
from parser.serializer import serialize_to_set_centric


RawWorkoutSession = TypedDict('RawWorkoutSession', {
    'date': str,
    'payload': str,
    'notes': str})

ParsedWorkoutSession = TypedDict('ParsedWorkoutSession', {
    'date': str,
    'parsed': list[Exercise],
    'notes': str})


class DataReader:
    """Handles reading training log files."""

    @staticmethod
    def read_file(file_path: str) -> str:
        """Read entire file as a string."""
        return Path(file_path).read_text(encoding='utf-8')

    @staticmethod
    def read_lines(file_path: str) -> list[str]:
        """Read file as lines, preserving line structure."""
        lines: list[str] = []
        with open(file_path, 'r') as f:
            while True:
                line = f.readline()
                if not line:
                    break
                lines.append(line.rstrip())
        return lines


class DataParser:
    """Handles parsing exercise data from text using ANTLR4."""

    @staticmethod
    def parse_raw_text(text: str) -> list[Exercise]:
        """
        Parse raw exercise text (without date filtering) into Exercise objects.

        Args:
            text: Exercise text in the format defined by training.g4

        Returns:
            List of parsed Exercise objects
        """
        input_stream = InputStream(text)
        lexer = trainingLexer(input_stream)
        token_stream = CommonTokenStream(lexer)
        token_stream.fill()
        parser = trainingParser(token_stream)
        tree = parser.workout()

        formatter = Formatter()
        formatter.visit(tree)
        return formatter.result

    @staticmethod
    def parse_file_filtered(file_path: str) -> list[Exercise]:
        """
        Parse a training log file, filtering out date lines (YYYY-MM-DD) and empty lines.

        Useful for simple single-session files where dates are metadata.

        Args:
            file_path: Path to the training log file

        Returns:
            List of parsed Exercise objects
        """
        content = DataReader.read_file(file_path)
        lines = content.split('\n')

        # Filter out date lines (YYYY-MM-DD) and empty lines
        filtered_lines = []
        for line in lines:
            line = line.strip()
            if line and not re.match(r'^\d{4}-\d{2}-\d{2}$', line):
                filtered_lines.append(line)

        filtered_content = '\n'.join(filtered_lines)
        return DataParser.parse_raw_text(filtered_content)


class SessionGrouper:
    """Handles grouping raw training log lines into workout sessions."""

    @staticmethod
    def group_by_sessions(lines: list[str]) -> list[RawWorkoutSession]:
        """
        Group lines into workout sessions by date and empty line separators.

        Session format:
        - First non-empty, non-note line is the date
        - Lines starting with # are notes
        - Remaining lines are exercise payload
        - Empty line marks session end

        Args:
            lines: List of lines from a training log file

        Returns:
            List of RawWorkoutSession objects with date, payload, and notes
        """
        sessions: list[RawWorkoutSession] = []
        current_payload: list[Any] = []
        notes: list[str] = []
        date: Any = None

        for line in lines:
            if line == '':
                if date is not None:
                    sessions.append(SessionGrouper._build_session(current_payload, date, notes))
                notes = []
                current_payload = []
                date = None
                continue

            if line.startswith('#'):
                notes.append(line)
                continue

            if date is None:
                date = line
                continue

            current_payload.append(line)

        # Don't forget the last session if file doesn't end with empty line
        if date is not None:
            sessions.append(SessionGrouper._build_session(current_payload, date, notes))

        return sessions

    @staticmethod
    def _build_session(payload: List[Any], date: Any, notes: list[str]) -> RawWorkoutSession:
        """Build a RawWorkoutSession from components."""
        payload.append("")
        assert date is not None, f"payload={payload}, date={date}, notes={notes}"
        return {
            'date': date,
            'payload': "\n".join(payload.copy()),
            'notes': "\n".join(notes.copy())
        }


class ExerciseParser:
    """Handles parsing workout sessions with exercise name standardization."""

    def __init__(self, standardizer: Optional[StandardizeName] = None):
        """
        Initialize exercise parser.

        Args:
            standardizer: StandardizeName instance for normalizing exercise names.
                         If None, creates a default instance.
        """
        self.standardizer = standardizer or StandardizeName()

    def parse_sessions(self, raw_sessions: list[RawWorkoutSession]) -> list[ParsedWorkoutSession]:
        """
        Parse raw workout sessions into exercises with standardized names.

        Args:
            raw_sessions: List of RawWorkoutSession objects

        Returns:
            List of ParsedWorkoutSession objects with parsed exercises
        """
        parsed_sessions: list[ParsedWorkoutSession] = []

        for session in raw_sessions:
            exercises = DataParser.parse_raw_text(session['payload'])
            self._standardize_names(exercises)

            parsed_session: ParsedWorkoutSession = {
                'date': session['date'],
                'parsed': exercises,
                'notes': session['notes']
            }
            parsed_sessions.append(parsed_session)

        return parsed_sessions

    def _standardize_names(self, exercises: list[Exercise]) -> None:
        """Apply name standardization to exercises in-place."""
        for exercise in exercises:
            exercise.name = self.standardizer.run(exercise.name)


class DataSerializer:
    """Handles serialization to different output formats."""

    @staticmethod
    def to_set_centric_json(exercises: list[Exercise], timestamp: Optional[Any] = None) -> dict[str, Any]:
        """
        Serialize exercises to set-centric JSON format.

        Args:
            exercises: List of Exercise objects
            timestamp: Optional datetime for the workout

        Returns:
            Dictionary in set-centric JSON format
        """
        return serialize_to_set_centric(exercises, timestamp)

    @staticmethod
    def to_tsv_rows(sessions: list[ParsedWorkoutSession]) -> list[list[str]]:
        """
        Serialize parsed sessions to TSV format (rows).

        Each row contains: date, name, set count, avg reps, weight

        Args:
            sessions: List of ParsedWorkoutSession objects

        Returns:
            List of lists, each inner list is a TSV row (including header)
        """
        rows: list[list[str]] = [['Date', 'Exercise', 'Sets', 'Avg Reps', 'Weight']]

        for session in sessions:
            for exercise in session['parsed']:
                for flattened_ex in exercise.flatten():
                    repetitions = [s.repetitions for s in flattened_ex.sets_]
                    weights = [s.weight.amount for s in flattened_ex.sets_]

                    assert weights[0] == (sum(weights) / len(weights)), \
                        f"Failed condition: Not all weights are equal in '{flattened_ex}'"

                    row = [
                        session['date'],
                        flattened_ex.name,
                        "{:d}".format(len(repetitions)),
                        "{:d}".format(int(sum(repetitions) / len(repetitions))),
                        "{:.1f}".format(flattened_ex.sets_[0].weight.amount).replace('.', ',')
                    ]
                    rows.append(row)

        return rows


class DataAccess:
    """
    High-level data access interface combining reading, parsing, and serialization.

    This is the main entry point for most use cases.
    """

    def __init__(self, standardizer: Optional[StandardizeName] = None):
        """
        Initialize data access layer.

        Args:
            standardizer: Optional StandardizeName instance. If None, creates default.
        """
        self.standardizer = standardizer or StandardizeName()
        self.exercise_parser = ExerciseParser(self.standardizer)

    def parse_single_file(self, file_path: str) -> list[Exercise]:
        """
        Parse a single training log file, filtering date lines.

        Suitable for simple files without session structure.

        Args:
            file_path: Path to the training log file

        Returns:
            List of standardized Exercise objects
        """
        exercises = DataParser.parse_file_filtered(file_path)
        self._standardize_names(exercises)
        return exercises

    def parse_multi_session_file(self, file_path: str) -> list[ParsedWorkoutSession]:
        """
        Parse a training log file with multiple sessions.

        Splits by date and empty line markers into sessions,
        parses each session, and standardizes names.

        Args:
            file_path: Path to the training log file

        Returns:
            List of ParsedWorkoutSession objects
        """
        lines = DataReader.read_lines(file_path)
        raw_sessions = SessionGrouper.group_by_sessions(lines)
        return self.exercise_parser.parse_sessions(raw_sessions)

    def _standardize_names(self, exercises: list[Exercise]) -> None:
        """Apply name standardization to exercises in-place."""
        for exercise in exercises:
            exercise.name = self.standardizer.run(exercise.name)
