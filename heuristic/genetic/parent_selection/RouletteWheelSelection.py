from random import choices

import numpy as np

from heuristic.genetic.Chromosome import Chromosome
from heuristic.genetic.parent_selection.ParentSelection import ParentSelection


class RouletteWheelSelection(ParentSelection):

    def select(self, population: [Chromosome]) -> [Chromosome]:
        # picks the first parent based on fitness (roulette wheel method)
        population_tot_fitness = sum([chromosome.get_tot_fitness() for chromosome in population])
        selection_probs = [chromosome.get_tot_fitness() / population_tot_fitness
                           for chromosome in population]
        parent1 = choices(population, weights=selection_probs, k=1)[0]

        # picks the second parent randomly within the population
        parent2 = population[np.random.randint(len(population))]
        return parent1, parent2
