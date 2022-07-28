from typing import Optional

import numpy as np
from matplotlib import pyplot as plt

from utils import Constraint
from utils.functions import overlap, binary_search, find_insertion_point
from .my_types import DTO, AR, ndarray


class Chromosome:
    """ A class that represents a possible solution of GeneticAlgorithm class """

    def __init__(self, capacity: float, ars: [AR], dtos: [DTO] = None) -> None:
        """ If no argument is given, creates an empty solution, otherwise creates a solution with given DTOs """
        if dtos is None:
            dtos = []
        # Loads DTOs
        self.dtos: [DTO] = sorted(dtos, key=lambda dto_: dto_['start_time'])
        # self.dto_ids: ndarray = np.array([dto['id'] for dto in self.dtos])
        # Loads ARs
        self.ars: [AR] = ars
        self.ar_ids: [int] = list(map(lambda ar: ar['id'], self.ars))

        if len(self.dtos) == 0:
            self.ars_served: ndarray = np.full(len(ars), False)
        else:
            self.ars_served: ndarray = np.isin(self.ar_ids, [dto['ar_id'] for dto in self.dtos])

        self.fitness: float = sum(self.get_priorities())
        self.tot_memory: float = sum(self.get_memories())

        self.capacity: float = capacity

    def print(self) -> None:
        """ Prints all info about the solution """
        print(self)

    def size(self) -> int:
        """ Returns the length of dto list """
        return len(self.dtos)

    def add_dto(self, dto: DTO) -> bool:
        """ Adds a DTO to the solution in start time order, updates total memory, fitness and ARs served.
            Returns True if the insertion """
        if np.any(self.dtos == dto):
            return False
        if len(self.dtos) == 0 or dto['stop_time'] < self.dtos[0]['start_time']:
            index = 0
        elif dto['start_time'] > self.dtos[-1]['stop_time']:
            index = len(self.dtos)
        else:
            index = find_insertion_point(dto, self.dtos, 0, len(self.dtos) - 1)

        self.dtos.insert(index, dto)
        self.tot_memory += dto['memory']
        self.fitness += dto['priority']
        self.ars_served[dto['ar_index']] = True
        # self.dto_ids = np.insert(self.dto_ids, index, dto['id'])
        return True

    def remove_dto(self, dto: DTO) -> bool:
        """ Removes a DTO from the solution """
        index = binary_search(dto, self.dtos, 0, len(self.dtos) - 1)
        if index == -1:
            return False
        return self.remove_dto_at(index)

    def remove_dto_at(self, index: int) -> bool:
        """ Removes the DTO at the given index """
        if index < 0 or index >= len(self.dtos):
            return False
        dto = self.dtos[index]
        self.dtos.pop(index)
        self.tot_memory -= dto['memory']
        self.fitness -= dto['priority']
        self.ars_served[dto['ar_index']] = False
        # self.dto_ids = np.delete(self.dto_ids, np.where(self.dto_ids == dto['id']))
        return True

    def get_memories(self) -> [float]:
        """ Returns the memory cost of each DTO in the solution """
        return list(map(lambda dto_: dto_['memory'], self.dtos))

    def get_priorities(self) -> [float]:
        """ Returns the priorities of the DTOs in the solution """
        return list(map(lambda dto_: dto_['priority'], self.dtos))

    def get_tot_memory(self) -> float:
        """ Returns the total memory occupied of the solution """
        return self.tot_memory

    def get_tot_fitness(self) -> float:
        """ Returns the fitness of the solution """
        return self.fitness

    def get_ars_served(self) -> [int]:
        """ Returns the ARs ids satisfied by the solution """
        return list(map(lambda dto: dto['ar_id'], self.dtos))

    def get_last_dto(self) -> Optional[DTO]:
        """ Returns the last DTO in the solution """
        if len(self.dtos) > 0:
            return self.dtos[-1]
        else:
            return None

    def keeps_feasibility(self, dto: DTO) -> bool:
        """ Returns True if the solution keeps feasibility if the DTO would be added """
        if self.ars_served[dto['ar_index']] \
                or self.get_tot_memory() + dto['memory'] > self.capacity:
            return False
        else:
            for dto_ in self.dtos:
                if overlap(dto, dto_):
                    return False
        return True

    def keeps_feasibility_except_memory(self, dto: DTO) -> bool:
        """ Returns True if the solution would respect all constraints except memory if the DTO would be added """
        return not self.ars_served[dto['ar_index']] \
            and not np.any([overlap(dto, dto_test) for dto_test in self.dtos])

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
        if constraint == Constraint.MEMORY:
            return self.get_tot_memory() < self.capacity
        elif constraint == Constraint.OVERLAP:
            for index in range(self.size() - 1):
                if overlap(self.dtos[index], self.dtos[index + 1]):
                    return False
            return True
        elif constraint == Constraint.SINGLE_SATISFACTION:
            return len(np.unique(self.get_ars_served())) == len(self.get_ars_served())

    def repair_memory(self):
        """ Repairs the memory constraint of the solution """
        while not self.is_feasible(Constraint.MEMORY):
            index = np.random.randint(self.size())
            self.remove_dto_at(index)

    def repair_overlap(self):
        """ Repairs the overlap constraint of the solution """
        while not self.is_feasible(Constraint.OVERLAP):
            i: int = 0
            while i < self.size() - 1:
                if overlap(self.dtos[i], self.dtos[i + 1]):
                    self.remove_dto_at(np.random.randint(i, i + 2))
                    i -= 1
                i += 1

    def repair_satisfaction(self):
        """ Repairs the single satisfaction constraint of the solution """
        while not self.is_feasible(Constraint.SINGLE_SATISFACTION):
            # ar_ids_served = np.array([dto['ar_id'] for dto in self.dtos])
            # values, counters = np.unique(ar_ids_served, return_counts=True)
            # dup = values[counters > 1]
            # for ar_id in dup:
            #     index = np.argwhere(ar_ids_served == ar_id)[0][0]
            #     self.remove_dto_at(index)

            index = np.random.randint(self.size())
            self.remove_dto_at(index)

    def plot_memory(self):
        """ Plots the memory of the solution """
        memories = []
        incremental_memory: float = 0
        for memory in self.get_memories():
            incremental_memory += memory
            memories.append(incremental_memory)
        xx = np.arange(self.size())
        plt.plot(xx, memories, 'r-')
        plt.title('Memory')
        plt.show()

    def __str__(self) -> str:
        return f'Fitness: {self.fitness},\nFeasible: {self.is_feasible()},\nMemory occupied: {self.tot_memory},' \
               f'\nDTOs taken: {self.dtos[:5]}...,\nARs served: {self.ars_served[:5]}...'
