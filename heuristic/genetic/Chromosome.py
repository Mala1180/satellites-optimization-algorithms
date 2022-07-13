import numpy
import numpy as np
from heuristic.genetic.vars import DTO, AR


class Chromosome:
    """ A class that represents a possible solution of GeneticAlgorithm class """

    def __init__(self, capacity: float, dtos: [DTO] = None) -> None:
        """ If no argument is given, creates an empty solution, otherwise a solution with given DTOs  """
        if dtos is None:
            dtos = []
        self.dtos: [DTO] = sorted(dtos, key=lambda dto_: dto_['start_time'])
        self.tot_fitness: float = sum(self.get_priorities())
        self.tot_memory: float = sum(self.get_memories())
        self.ars_served = np.array([dto_['ar_id'] for dto_ in self.dtos])
        self.capacity: float = capacity

    def __str__(self) -> str:
        return f'Fitness: {self.tot_fitness},\nFeasible: {self.is_feasible()},\nMemory occupied: {self.tot_memory},' \
               f'\nDTOs taken: {self.dtos[:5]}...,\nARs served: {self.ars_served[:5]}...'

    def print(self) -> None:
        """ Prints all info about the solution """
        print(self)

    def size(self) -> int:
        """ Returns the length of dto list """
        return len(self.dtos)

    def add_dto(self, dto: DTO) -> bool:
        """ Adds a DTO to the solution in start time order, updates total memory, fitness and ARs served.
            Returns True if the insertion """
        if len(self.dtos) == 0 or dto['stop_time'] < self.dtos[0]['start_time']:
            index = 0
        elif dto['start_time'] > self.dtos[-1]['stop_time']:
            index = len(self.dtos)
        else:
            condition = [dto['start_time'] > self.dtos[i]['stop_time']
                         and dto['stop_time'] < self.dtos[i + 1]['start_time']
                         for i in range(len(self.dtos) - 1)]
            if not np.any(condition):
                return False
            insert_point = np.extract(condition, self.dtos)
            index = self.dtos.index(insert_point) + 1

        self.dtos.insert(index, dto)
        self.tot_memory += dto['memory']
        self.tot_fitness += dto['priority']
        self.ars_served = np.append(self.ars_served, dto['ar_id'])
        return True

    def remove_dto(self, dto: DTO) -> bool:
        if len(self.dtos) == 0 or not np.isin(dto, self.dtos):
            return False
        index = np.searchsorted(self.dtos, dto)
        self.dtos = np.delete(self.dtos, index)
        self.tot_memory -= dto['memory']
        self.tot_fitness -= dto['priority']
        self.ars_served = np.delete(self.ars_served, np.where(self.ars_served == dto['ar_id']))
        return True

    def get_memories(self) -> [float]:
        return list(map(lambda dto_: dto_['memory'], self.dtos))

    def get_priorities(self) -> [float]:
        return list(map(lambda dto_: dto_['priority'], self.dtos))

    def get_tot_memory(self) -> float:
        return self.tot_memory

    def get_tot_fitness(self) -> float:
        return self.tot_fitness

    def get_max_priority(self) -> float:
        return float(np.max(np.array(self.get_priorities())))

    def get_ars_served(self) -> []:
        return self.ars_served

    def get_last_dto(self):
        if len(self.dtos) > 0:
            return self.dtos[-1]
        else:
            return None

    def keeps_feasibility(self, dto: DTO) -> bool:
        """ Returns True if the solution keeps feasibility if the DTO would be added """
        return not np.isin(dto['ar_id'], self.get_ars_served()) \
               and self.get_tot_memory() + dto['memory'] <= self.capacity \
               and not np.any([self.overlap(dto, dto_test) for dto_test in self.dtos])

    def is_feasible(self) -> bool:
        """ Checks if the solution is feasible or not """
        # memory constraint check
        if self.get_tot_memory() > self.capacity:
            return False

        # overlap constraint check
        for dto1 in self.dtos:
            for dto2 in self.dtos:
                if self.overlap(dto1, dto2) and dto1 != dto2:
                    return False

        # single satisfaction check
        if len(np.unique(self.get_ars_served())) != len(self.get_ars_served()):
            return False
        return True

    @staticmethod
    def overlap(event1: DTO, event2: DTO):
        """ Returns True if events overlap, False otherwise """
        return event1['start_time'] <= event2['stop_time'] and event1['stop_time'] >= event2['start_time']
