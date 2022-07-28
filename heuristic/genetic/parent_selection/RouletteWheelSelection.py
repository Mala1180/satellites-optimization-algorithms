from random import choices

import numpy as np

from heuristic.genetic.Chromosome import Chromosome
from heuristic.genetic.parent_selection.ParentSelection import ParentSelection


class RouletteWheelSelection(ParentSelection):

    def __init__(self, population: [Chromosome]):
        self.population = population
        population_tot_fitness = sum([chromosome.get_tot_fitness() for chromosome in population])
        self.selection_probs = [chromosome.get_tot_fitness() / population_tot_fitness
                                for chromosome in population]

    def select(self) -> (Chromosome, Chromosome):
        # picks the first parent based on fitness (roulette wheel method)
        parent1 = choices(self.population, weights=self.selection_probs, k=1)[0]

        # picks the second parent randomly within the population
        parent2 = self.population[np.random.randint(len(self.population))]
        return parent1, parent2
