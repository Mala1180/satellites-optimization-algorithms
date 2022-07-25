from abc import ABC, abstractmethod

from heuristic.genetic.Chromosome import Chromosome


class ParentSelection(ABC):

    @abstractmethod
    def select(self, population: [Chromosome]) -> [Chromosome]:
        pass
