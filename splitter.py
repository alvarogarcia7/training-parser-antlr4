import copy
import csv
from typing import Any, TextIO, TypedDict

from antlr4 import InputStream, CommonTokenStream

from dist.trainingLexer import trainingLexer
from dist.trainingParser import trainingParser
from parser import Formatter, Exercise, StandardizeName


class Splitter:
    def _parse(self, param: str) -> Any:
        input_stream = InputStream(param)
        lexer = trainingLexer(input_stream)
        token_stream = CommonTokenStream(lexer)
        token_stream.fill()
        parser = trainingParser(token_stream)
        tree = parser.workout()

        formatter = Formatter()
        formatter.visit(tree)
        result = formatter.result
        return result

    def main(self) -> None:
        lines = self._read_all_lines('data.txt')

        Parsing1 = TypedDict('Parsing1', {
            'date': str,
            'payload': str,
            'notes': str})

        jobs: list[Parsing1] = []
        current = []
        notes: list[str] = []
        date: Any = None
        for idx in range(len(lines)):
            if lines[idx] == '':
                current.append("")
                assert date is not None
                job: Parsing1 = {'date': date,
                                 'payload': "\n".join(current.copy()),
                                 'notes': "\n".join(notes.copy())
                                 }
                jobs.append(job)
                current = []
                date = None
                continue
            if lines[idx].startswith('#'):
                notes.append(lines[idx])
                continue
            if date is None:
                date = lines[idx]
                continue
            current.append(lines[idx])

        Parsing2 = TypedDict('Parsing2', {
            'date': str,
            'parsed': list[Exercise],
            'notes': str})
        jobs2: list[Parsing2] = []
        for job in jobs:
            job_tmp: Any = copy.deepcopy(job)
            job_tmp['parsed'] = self._parse(job['payload'])
            jobs2.append(job_tmp)

        file_path_: str = 'output.csv'
        renamer = StandardizeName()
        with open(file_path_, mode='w+', newline='') as csvfile:
            csv_writer = csv.writer(csvfile, delimiter='\t', quotechar='"')
            for job2 in jobs2:
                row: Exercise
                for row in job2['parsed']:
                    repetitions_ = [i['repetitions'] for i in row.sets_]
                    weights = [i['weight']['amount'] for i in row.sets_]
                    weights_ = weights[0] == sum(weights) / len(weights)
                    if not weights_:
                        print(f"Failed for {row}")
                        assert False
                    csv_writer.writerow([
                        job2['date'],
                        renamer.run(row.name),
                        None,
                        "{:d}".format(len(repetitions_)),
                        "{:d}".format(int(sum(repetitions_) / len(repetitions_))),
                        "{:.1f}".format(row.sets_[0]['weight']['amount']).replace('.', ',')
                    ]
                    )

    def _read_all_lines(self, file_name: str) -> list[str]:
        lines: list[str] = []
        file_path: TextIO
        with open(file_name, 'r') as file_path:
            while True:
                line = file_path.readline()
                if not line:
                    break
                lines.append(line.rstrip())
        return lines


if __name__ == "__main__":
    Splitter().main()
