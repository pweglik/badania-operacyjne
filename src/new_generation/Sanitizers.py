from abc import ABC, abstractmethod
import functools
import inspect
from typing import Callable, Optional, ParamSpec, Type, TypeVar, Union
from common.Genotype import Genotype
from common.Line import Line


P = ParamSpec("P")
GenType = TypeVar("GenType", bound=Genotype)
LineType = TypeVar("LineType", bound=Line)
GL = Union[GenType, LineType]


class Sanitizer(ABC):
    def __init__(self, best_paths) -> None:
        super().__init__()
        self.best_paths = best_paths

    @abstractmethod
    def sanitizeLine(self, line: Line) -> Optional[Line]:
        pass

    @abstractmethod
    def sanitizeGenotype(self, genotype: Genotype) -> Optional[Genotype]:
        pass


class BasicSanitizer(Sanitizer):
    def sanitizeLine(self, line: Line) -> Optional[Line]:
        if line.stops_no <= 0:
            return None
        new_stops = []

        prev = None
        for el in line.stops:
            if el != prev:
                new_stops.append(el)
            prev = el

        return Line(new_stops, self.best_paths)

    def sanitizeGenotype(self, genotype: Genotype) -> Optional[Genotype]:
        new_lines = [
            line for line in map(self.sanitizeLine, genotype.lines) if line is not None
        ]
        if len(new_lines) <= 0:
            return None
        return Genotype(new_lines)


class RejectingSanitizer(Sanitizer):
    def __init__(self, criterium_sanitizer: Sanitizer) -> None:
        self.delegate = criterium_sanitizer

    def sanitizeLine(self, line: Line) -> Optional[Line]:
        return line if self.delegate.sanitizeLine(line) == line else None

    def sanitizeGenotype(self, genotype: Genotype) -> Optional[Genotype]:
        return (
            genotype if self.delegate.sanitizeGenotype(genotype) == genotype else None
        )

