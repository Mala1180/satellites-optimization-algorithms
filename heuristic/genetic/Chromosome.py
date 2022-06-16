import numpy as np
from heuristic.genetic.vars import DTO


class Chromosome:
    """ A class that represents a possible solution of GeneticAlgorithm class """

    def __init__(self, dtos: [DTO] = None) -> None:
        """ If no argument is given, creates an empty solution, otherwise a solution with given DTOs  """
        if dtos is None:
            dtos = []
        self.dtos = dtos
        self.fitness = 0

    def print(self) -> None:
        print(self.dtos)

    def count(self) -> int:
        return len(self.dtos)

    def add_dto(self, dto: DTO) -> None:
        self.dtos.append(dto)

    def add_dto_at(self, dto: DTO, index: int) -> None:
        self.dtos.insert(index, dto)

    def remove_dto(self, dto: DTO) -> None:
        self.dtos.remove(dto)

    def remove_dto_at(self, index: int) -> None:
        self.dtos.pop(index)

    def get_memories(self) -> [float]:
        return list(map(lambda dto_: dto_['memory'], self.dtos))

    def get_priorities(self) -> [float]:
        return list(map(lambda dto_: dto_['priority'], self.dtos))

    def get_tot_memory(self) -> float:
        return float(np.sum(np.array(self.get_memories())))

    def get_tot_priority(self) -> float:
        return float(np.sum(np.array(self.get_priorities())))

    def get_min_priority(self) -> float:
        return float(np.min(np.array(self.get_priorities())))

    def get_max_priority(self) -> float:
        return float(np.max(np.array(self.get_priorities())))

    @staticmethod
    def overlap(event1: DTO, event2: DTO):
        return event1['start_time'] <= event2['stop_time'] and event1['stop_time'] >= event2['start_time']
