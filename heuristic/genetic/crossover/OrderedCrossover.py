from random import choice

from heuristic.genetic.Chromosome import Chromosome
from heuristic.genetic.crossover.Crossover import Crossover


class OrderedCrossover(Crossover):

    def crossover(self, parent1: Chromosome, parent2: Chromosome) -> [Chromosome]:
        random = choice(range(0, len(parent1.dtos)))
        stop_time = parent1.dtos[random]['stop_time']

        i = 0
        while i < len(parent2.dtos) and parent2.dtos[i]['start_time'] <= stop_time:
            i += 1
        return parent1.dtos[:random] + parent2.dtos[i:]
