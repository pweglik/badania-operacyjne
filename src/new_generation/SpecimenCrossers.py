import random as rd
from src.Genotype import Genotype


class GenotypeCrosser:
    def merge_genotypes(self, genotype1: Genotype, genotype2: Genotype) -> Genotype:
        lines1 = rd.choices(genotype1.lines, k=rd.randint(0, len(genotype1.lines)))
        lines2 = rd.choices(genotype2.lines, k=rd.randint(0, len(genotype2.lines)))

        return Genotype(lines1 + lines2)


