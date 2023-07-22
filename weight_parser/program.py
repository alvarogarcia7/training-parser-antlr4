from __future__ import annotations

from functools import reduce
from typing import Any, Dict


def chain(arg: object, *funcs: Any) -> object:
    return reduce(lambda r, f: f(r), funcs, arg)


class SingleMeasurementWeightParser:

    def __init__(self, year: str):
        self.year = year

    def _select_only_element(self, list: list[Any]) -> Any:
        assert len(list) == 1
        return list[0]

    def _to_spanish_locale(self, value: str) -> str:
        return value.replace(',', '').replace('.', ',')

    def _select_before_space(self, ele: str) -> str:
        return ele.split(" ")[0].strip()

    def parse(self, text: str) -> dict[str, str]:
        lines = text.splitlines()

        try:
            bodv_score = chain(lines,
                               lambda ele: filter(lambda line: "Bodv score" in line, ele),
                               lambda ele: self._find_next(ele, lines),
                               lambda ele: ele.strip())
        except Exception:
            pass

        try:
            bodv_score = chain(lines,
                               lambda ele: filter(lambda line: "Body score" in line, ele),
                               lambda ele: self._find_next(ele, lines),
                               lambda ele: ele.strip())
        except Exception:
            pass

        try:
            bodv_score = chain(lines,
                               lambda ele: filter(lambda line: "Bod score" in line, ele),
                               lambda ele: self._find_next(ele, lines),
                               lambda ele: ele.strip())
        except Exception:
            pass

        assert bodv_score
        result: dict[str, str] = {'visceral fat': str(chain(lines,
                                                            lambda ele: self.select_single_then_split(ele,
                                                                                                      "Visceral fat")
                                                            )),
                                  'basal metabolism': str(chain(lines,
                                                                lambda lines: self.select_single_then_split(lines,
                                                                                                            "Basal metabolism"),
                                                                lambda ele: self._select_before_space(ele),
                                                                lambda ele: self._to_spanish_locale(ele))),
                                  'body fat': str(chain(lines,
                                                        lambda ele: self.select_single_then_split(ele, "Body fat"),
                                                        lambda ele: ele.removesuffix('%'),
                                                        lambda ele: ele.strip(),
                                                        lambda ele: self._select_before_space(ele),
                                                        lambda ele: self._to_spanish_locale(ele)))
            ,
                                  'muscle': str(chain(lines,
                                                      lambda lines: self.select_single_then_split(lines, "Muscle"),
                                                      lambda ele: self._select_before_space(ele),
                                                      lambda ele: self._to_spanish_locale(ele))),
                                  'protein': str(chain(lines,
                                                       lambda lines: self.select_single_then_split(lines, "Protein"),
                                                       lambda ele: ele.removesuffix('%'),
                                                       lambda ele: self._to_spanish_locale(ele))),

                                  'water': str(chain(lines,
                                                     lambda lines: self.select_single_then_split(lines, "Water"),
                                                     lambda ele: ele.removesuffix('%'),
                                                     lambda ele: self._to_spanish_locale(ele))),
                                  'bone mass': str(chain(lines,
                                                         lambda lines: self.select_single_then_split(lines,
                                                                                                     "Bone mass"),
                                                         lambda ele: self._select_before_space(ele),
                                                         lambda ele: self._to_spanish_locale(ele))),
                                  'bmi': str(chain(lines,
                                                   lambda lines: self.select_single_then_split(lines, "BMI"),
                                                   lambda ele: self._select_before_space(ele),
                                                   lambda ele: self._to_spanish_locale(ele),
                                                   lambda ele: str(ele)
                                                   )),
                                  'weight': str(chain(lines,
                                                      lambda ele: filter(lambda line: "Weight" in line, ele),
                                                      lambda ele: self._find_previous(ele, lines),
                                                      lambda ele: ele.strip(),
                                                      lambda ele: self._select_before_space(ele),
                                                      lambda ele: self._to_spanish_locale(ele),
                                                      lambda ele: str(ele)
                                                      )),
                                  'date': str(chain(lines,
                                                    lambda ele: filter(lambda line: "Weight" in line, ele),
                                                    lambda ele: self._find_previous(ele, lines),
                                                    lambda ele: self._find_previous([ele], lines),  # type: ignore
                                                    lambda ele: ele.split(" ")[0],
                                                    lambda ele: f"{ele.strip()}/{self.year}",
                                                    lambda ele: "/".join(ele.split("/")[0:3]),
                                                    lambda ele: ele.strip(),
                                                    lambda ele: str(ele)
                                                    )),
                                  'body score': str(bodv_score),
                                  'body type': str(chain(lines,
                                                         lambda ele: filter(lambda line: "Body type" in line, ele),
                                                         lambda ele: self._find_previous(ele, lines),
                                                         lambda ele: ele.strip(),
                                                         lambda ele: str(ele)
                                                         ))}

        return result

    def _find_previous(self, line: str, lines: list[str]) -> str:
        element = self._select_only_element(list(line))
        return lines[lines.index(element) - 1]

    def _find_next(self, line: str, lines: list[str]) -> str:
        element = self._select_only_element(list(line))
        return lines[lines.index(element) + 1]

    def select_single_then_split(self, lines: list[str], keyword: str) -> str:
        o = chain(lines, lambda ele: filter(lambda line: keyword in line, ele), lambda ele: list(ele),
                  self._select_only_element, lambda ele: ele.split(keyword)[-1], lambda ele: ele.strip())
        return str(o)


class WeightParser:
    def __init__(self, end: str, single_parser: SingleMeasurementWeightParser):
        self.end = end
        self.single_parser = single_parser

    def parse(self, lines: list[str]) -> list[dict[str, Any]]:
        current: list[Any] = []
        notes: list[list[str]] = []
        for line in lines:
            if line:
                current.append(line)
            if self.end in line:
                notes.append(current)
                current = []

        result = []
        for note in notes:
            parse = self.single_parser.parse("\n".join(note))
            result.append(parse)
        return result
