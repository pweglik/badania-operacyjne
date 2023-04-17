import random
from copy import deepcopy

import networkx as nx

from src.Genotype import Genotype
from src.new_generation.Mutators import LineMutator, GenotypeMutator
from src.new_generation.SpecimenCrossers import GenotypeCrosser
from src.params import *


def new_generation_random(
    population_with_fitness: list[tuple[Genotype, float]],
    new_generation_size: int,
    line_mutator: LineMutator,
    genotype_mutator: GenotypeMutator,
    genotype_crosser: GenotypeCrosser,
) -> list[Genotype]:
    # extract organisms only (ignore fitness) from population_with_fitness
    new_generation: list[Genotype] = [
        organism_with_fitness[0] for organism_with_fitness in population_with_fitness
    ]

    counter = 0
    while len(new_generation) < new_generation_size:
        # generate new specimen from best ones
        if random.random() < CHANCE_MERGE_SPECIMEN:
            g_new = genotype_crosser.merge_genotypes(
                new_generation[0], new_generation[1]
            )

            new_generation.append(g_new)

        # get organism (clone it, don't modify original) by
        # looping over population_with_fitness with counter index
        organism: Genotype = deepcopy(
            population_with_fitness[counter % len(population_with_fitness)][0]
        )

        # (operating on clone)

        # run line mutators
        # get random line, remove it, run line mutator on it, add it back
        random_line = random.sample(organism.lines, 1)[0]
        organism.lines.remove(random_line)

        if random.random() < CHANCE_ROT_RIGHT:
            random_line = line_mutator.rotation_to_right(random_line)
            dprint("ROT RIGHT", len(random_line.stops))

        if random.random() < CHANCE_ROT_CYCLE:
            random_line = line_mutator.cycle_rotation(random_line)
            dprint("ROT CYCLE", len(random_line.stops))

        if random.random() < CHANCE_INVERT:
            random_line = line_mutator.invert(random_line)
            dprint("INVERT", len(random_line.stops))

        if len(random_line.stops) > 0:
            organism.lines.append(random_line)

        if len(organism.lines) == 0:
            continue

        # run genotype mutators

        if random.random() < CHANCE_ERASE_LINE:
            organism = genotype_mutator.erase_line(organism)
            dprint("ERASE", organism.get_line_stops_count_summary())

        if len(organism.lines) == 0:
            continue

        if random.random() < CHANCE_CREATE_LINE:
            organism = genotype_mutator.create_line(organism)
            dprint("CREATE", organism.get_line_stops_count_summary())

        # split some line
        if random.random() < CHANCE_SPLIT:
            organism = genotype_mutator.split_line(organism)
            dprint("SPLIT", organism.get_line_stops_count_summary())

        # merge some lines
        if random.random() < CHANCE_MERGE and len(organism.lines) > 1:
            organism = genotype_mutator.merge_lines(organism)
            dprint("MERGE", organism.get_line_stops_count_summary())

        if random.random() < CHANCE_CYCLE:
            organism = genotype_mutator.cycle_stops_shift(organism)
            dprint("CYCLE", organism.get_line_stops_count_summary())

        # add clone to new generation
        new_generation.append(organism)

        counter += 1

    return new_generation
