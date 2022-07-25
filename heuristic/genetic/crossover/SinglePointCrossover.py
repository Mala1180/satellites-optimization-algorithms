import numpy as np

from heuristic.genetic.Chromosome import Chromosome
from heuristic.genetic.crossover.Crossover import Crossover


class SinglePointCrossover(Crossover):

    def crossover(self, parent1: Chromosome, parent2: Chromosome) -> [Chromosome]:
        index = np.random.randint(0, len(parent1.dtos))
        return parent1.dtos[:index] + parent2.dtos[index:]
