import random
from dataclasses import dataclass

from Sanitizers import Sanitizer
from src.common.Genotype import Genotype
from src.new_generation.Mutators import LineMutator, GenotypeMutator
from src.new_generation.SpecimenCrossers import GenotypeCrosser
from src.common.params import (
    dprint,
)


@dataclass
class NewGenerationRandomParams:
    chance_create_line: float
    chance_cycle: float
    chance_erase_line: float
    chance_invert: float
    chance_merge: float
    chance_merge_specimen: float
    chance_rot_cycle: float
    chance_rot_right: float
    chance_split: float


def new_generation_random(
    population_with_fitness: list[tuple[Genotype, float]],
    new_generation_size: int,
    line_mutator: LineMutator,
    genotype_mutator: GenotypeMutator,
    genotype_crosser: GenotypeCrosser,
    sanitizer: Sanitizer,
    params: NewGenerationRandomParams,
) -> list[Genotype]:
    # extract organisms only (ignore fitness) from population_with_fitness
    new_generation: list[Genotype] = [
        organism_with_fitness[0] for organism_with_fitness in population_with_fitness
    ]

    counter = 0
    while len(new_generation) < new_generation_size:
        if random.random() < params.chance_merge_specimen:
            # cross 2 random genotypes
            g_new = genotype_crosser.merge_genotypes(*random.sample(new_generation, 2))

            new_generation.append(g_new)

        # get organism (don't clone, mutators don't modify original data) by
        # looping over population_with_fitness with counter index
        organism: Genotype = population_with_fitness[
            counter % len(population_with_fitness)
        ][0]

        # run line mutators

        if random.random() < params.chance_rot_right:
            organism = LineMutator.mutate_one_line_out_of_organism(
                organism, sanitizer, line_mutator.rotation_to_right
            )
            # dprint("ROT RIGHT", len(random_line.stops))

        if random.random() < params.chance_rot_cycle:
            organism = LineMutator.mutate_one_line_out_of_organism(
                organism, sanitizer, line_mutator.cycle_rotation
            )
            # dprint("ROT CYCLE", len(random_line.stops))

        if random.random() < params.chance_invert:
            organism = LineMutator.mutate_one_line_out_of_organism(
                organism, sanitizer, line_mutator.invert
            )
            # dprint("INVERT", len(random_line.stops))

        # run genotype mutators

        if random.random() < params.chance_erase_line:
            organism = genotype_mutator.erase_line(organism)
            dprint("ERASE", organism.get_line_stops_count_summary())

        organism = sanitizer.sanitizeGenotype(organism)
        if organism is None:
            continue

        if random.random() < params.chance_create_line:
            organism = genotype_mutator.create_line(organism)
            dprint("CREATE", organism.get_line_stops_count_summary())

        # split some line
        if random.random() < params.chance_split:
            organism = genotype_mutator.split_line(organism)
            dprint("SPLIT", organism.get_line_stops_count_summary())

        # merge some lines
        if random.random() < params.chance_merge and len(organism.lines) > 1:
            organism = genotype_mutator.merge_lines(organism)
            dprint("MERGE", organism.get_line_stops_count_summary())

        if random.random() < params.chance_cycle:
            organism = genotype_mutator.cycle_stops_shift(organism)
            dprint("CYCLE", organism.get_line_stops_count_summary())

        organism = sanitizer.sanitizeGenotype(organism)
        if organism is None:
            continue

        new_generation.append(organism)

        counter += 1

    return new_generation
