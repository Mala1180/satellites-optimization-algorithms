import numpy as np

from typing import Optional
from heuristic.genetic.vars import DTO, ndarray
from utils.Constraint import Constraint


class Chromosome:
    """ A class that represents a possible solution of GeneticAlgorithm class """

    def __init__(self, capacity: float, dtos: [DTO] = None) -> None:
        """ If no argument is given, creates an empty solution, otherwise a solution with given DTOs  """
        if dtos is None:
            dtos = []
        self.dtos: [DTO] = sorted(dtos, key=lambda dto_: dto_['start_time'])
        self.dto_ids: ndarray = np.array([dto_['id'] for dto_ in self.dtos])
        self.tot_fitness: float = sum(self.get_priorities())
        self.tot_memory: float = sum(self.get_memories())
        self.ars_served: ndarray = np.array([dto_['ar_id'] for dto_ in self.dtos])
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
            if not np.any(condition) or np.isin(dto['id'], self.dto_ids):
                return False
            insert_point = np.extract(condition, self.dtos)[0]
            index = self.dtos.index(insert_point) + 1

        self.dtos.insert(index, dto)
        self.tot_memory += dto['memory']
        self.tot_fitness += dto['priority']
        self.ars_served = np.append(self.ars_served, dto['ar_id'])
        self.dto_ids = np.insert(self.dto_ids, index, dto['id'])
        return True

    def remove_dto(self, dto: DTO) -> bool:
        if len(self.dtos) == 0 or np.isin(dto['id'], self.dto_ids):
            return False
        index = np.where(self.dto_ids == dto['id'])
        return self.remove_dto_at(index)

    def remove_dto_at(self, index: int) -> bool:
        """ Removes the DTO at the given index """
        if index < 0 or index >= len(self.dtos):
            return False
        dto = self.dtos[index]
        self.dtos.pop(index)
        self.tot_memory -= dto['memory']
        self.tot_fitness -= dto['priority']
        self.ars_served = np.delete(self.ars_served, np.where(self.ars_served == dto['ar_id']))
        self.dto_ids = np.delete(self.dto_ids, np.where(self.ars_served == dto['id']))
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

    def get_last_dto(self) -> Optional[DTO]:
        if len(self.dtos) > 0:
            return self.dtos[-1]
        else:
            return None

    def keeps_feasibility(self, dto: DTO) -> bool:
        """ Returns True if the solution keeps feasibility if the DTO would be added """
        return not np.isin(dto['ar_id'], self.get_ars_served()) \
            and self.get_tot_memory() + dto['memory'] <= self.capacity \
            and not np.any([self.overlap(dto, dto_test) for dto_test in self.dtos])

    def keeps_feasibility_except_memory(self, dto: DTO) -> bool:
        """ Returns True if the solution would respect all constraints except memory if the DTO would be added """
        return not np.isin(dto['ar_id'], self.get_ars_served()) \
            and not np.any([self.overlap(dto, dto_test) for dto_test in self.dtos])

    def is_feasible(self, constraint: Constraint = None) -> bool:
        """ Checks if the solution is feasible or not.
            If constraint is given, it checks if the solution keeps the constraint,
            otherwise it checks all constraints. """
        if constraint is None:
            if not self.constraint_feasible(Constraint.MEMORY):
                return False

            if not self.constraint_feasible(Constraint.OVERLAP):
                return False

            if not self.constraint_feasible(Constraint.SINGLE_SATISFACTION):
                return False

            return True
        else:
            if self.constraint_feasible(constraint):
                return True
            else:
                return False

    def constraint_feasible(self, constraint: Constraint) -> bool:
        """ Returns true if the solution respects the given constraint, false otherwise """
        match constraint:
            case Constraint.MEMORY:
                return self.get_tot_memory() < self.capacity
            case Constraint.OVERLAP:
                for dto1 in self.dtos:
                    for dto2 in self.dtos:
                        if self.overlap(dto1, dto2) and dto1 != dto2:
                            return False
                return True
            case Constraint.SINGLE_SATISFACTION:
                return len(np.unique(self.get_ars_served())) == len(self.get_ars_served())

    def repair_memory(self):
        while not self.is_feasible(Constraint.MEMORY):
            dto = min(self.dtos, key=lambda dto_: dto_['priority'])
            index = np.where(self.dto_ids == dto['id'])[0][0]
            self.remove_dto_at(index)

    @staticmethod
    def overlap(event1: DTO, event2: DTO):
        """ Returns True if events overlap, False otherwise """
        return event1['start_time'] <= event2['stop_time'] and event1['stop_time'] >= event2['start_time']
