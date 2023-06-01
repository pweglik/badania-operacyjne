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

    def sanitize(
        self, _fn: Callable[P, GL] | Callable[P, Optional[GL]]
    ) -> Callable[P, Optional[GL]]:
        if inspect.signature(_fn).return_annotation in [Line, Optional[Line]]:

            @functools.wraps(_fn)
            def lineWrapper(*args: P.args, **kwds: P.kwargs) -> Optional[Line]:
                line = _fn(*args, **kwds)
                if line is not None:
                    return self.sanitizeLine(line)
                else:
                    return None

            return lineWrapper

        if inspect.signature(_fn).return_annotation in [Genotype, Optional[Genotype]]:

            @functools.wraps(_fn)
            def genotypeWrapper(*args: P.args, **kwds: P.kwargs) -> Optional[Genotype]:
                genotype = _fn(*args, **kwds)
                if genotype is not None:
                    return self.sanitizeGenotype(genotype)
                else:
                    return None

            return genotypeWrapper

        return _fn


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


if __name__ == "__main__":
    sanitizer = BasicSanitizer([])

    @sanitizer.sanitize
    def test(_: Genotype) -> Genotype:
        return Genotype([])

    print(test.__name__)
    print(test(Genotype([])))
