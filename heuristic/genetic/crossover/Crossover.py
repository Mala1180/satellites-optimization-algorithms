from abc import ABC, abstractmethod

from heuristic.genetic.Chromosome import Chromosome


class Crossover(ABC):

    @abstractmethod
    def crossover(self, parent1: Chromosome, parent2: Chromosome) -> [Chromosome]:
        pass
