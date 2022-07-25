from random import sample

from heuristic.genetic.Chromosome import Chromosome
from heuristic.genetic.crossover.Crossover import Crossover


class MultiPointCrossover(Crossover):

    def crossover(self, parent1: Chromosome, parent2: Chromosome) -> [Chromosome]:
        rand1, rand2 = sample(range(0, len(parent1.dtos)), 2)
        i1, i2 = (rand1, rand2) if rand1 <= rand2 else (rand2, rand1)
        return parent1.dtos[:i1] + parent2.dtos[i1:i2] + parent1.dtos[i2:]
