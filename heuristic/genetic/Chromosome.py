import collections
from random import shuffle, sample
from typing import Optional

import numpy as np
from matplotlib import pyplot as plt

from utils import Constraint
from utils.functions import overlap, binary_search, find_insertion_point
from .my_types import DTO, AR, DLO, ndarray


class Chromosome:
    """ A class that represents a possible solution of GeneticAlgorithm class """

    def __init__(self, capacity: float, ars: [AR], dtos: [DTO] = None,
                 dlos: [DLO] = None, downlink_rate: float = None) -> None:
        """ If no argument is given, creates an empty solution, otherwise creates a solution with given DTOs """
        if dtos is None:
            dtos = []
        if dlos is None:
            dlos = []
        # Loads DTOs
        self.dtos: [DTO] = sorted(dtos, key=lambda dto_: dto_['start_time'])
        # Loads ARs
        self.ars: [AR] = ars
        self.ar_ids: [int] = list(map(lambda ar: ar['id'], self.ars))
        # Loads DLOs
        self.dlos = sorted(dlos, key=lambda dlo_: dlo_['start_time'])
        for dlo in self.dlos:
            dlo['downloaded_dtos'] = []

        if len(self.dtos) == 0:
            self.ars_served: ndarray = np.full(len(ars), False)
        else:
            self.ars_served: ndarray = np.isin(self.ar_ids, [dto['ar_id'] for dto in self.dtos])

        self.fitness: float = sum(self.get_priorities())
        self.tot_memory: float = sum(self.get_memories())

        self.capacity: float = capacity
        self.downlink_rate: float = downlink_rate

    def print(self) -> None:
        """ Prints all info about the solution """
        print(self)

    def size(self) -> int:
        """ Returns the length of dto list """
        return len(self.dtos)

    def add_dto(self, dto: DTO) -> bool:
        """ Adds a DTO to the solution in start time order, updates total memory, fitness and ARs served.
            Returns True if the insertion """
        if len(self.dtos) == 0 or dto['start_time'] <= self.dtos[0]['start_time']:
            index = 0
        elif dto['start_time'] >= self.dtos[-1]['start_time']:
            index = len(self.dtos)
        else:
            index = binary_search(dto, self.dtos)
            if index != -1:
                pass
                # return False
            else:
                index = find_insertion_point(dto, self.dtos)

        self.dtos.insert(index, dto)
        self.tot_memory += dto['memory']
        self.fitness += dto['priority']
        self.ars_served[dto['ar_index']] = True

        # if len(self.dlos) > 0:
        #     for j in sample(list(range(0, len(self.dlos))), len(self.dlos)):
        #         if self.dlos[j]['start_time'] > dto['stop_time'] and self.is_dto_downloadable(dto, self.dlos[j]):
        #             self.dlos[j]['downloaded_dtos'].append(dto)
        #             break
        return True

    def remove_dto(self, dto: DTO) -> bool:
        """ Removes a DTO from the solution """
        index = binary_search(dto, self.dtos)
        if index == -1:
            return False
        # if len(self.dlos) > 0:
        #     for dlo in self.dlos:
        #         index = binary_search(dto, dlo['downloaded_dtos'])
        #         if index != -1:
        #             dlo['downloaded_dtos'].pop(index)
        return self.remove_dto_at(index)

    def remove_dto_at(self, index: int):
        """ Removes the DTO at the given index, raises an exception if the index is out of bounds """
        if index < 0 or index >= len(self.dtos):
            print(f'Index:{index}, len(self.dtos):{len(self.dtos)}')
            raise IndexError("Index out of range")
        dto = self.dtos[index]
        self.dtos.pop(index)
        self.tot_memory -= dto['memory']
        self.fitness -= dto['priority']
        self.ars_served[dto['ar_index']] = False
        # self.dto_ids = np.delete(self.dto_ids, np.where(self.dto_ids == dto['id']))

    def get_memories(self) -> [float]:
        """ Returns the memory costs of each DTO in the solution """
        return list(map(lambda dto_: dto_['memory'], self.dtos))

    def get_dto_ids(self) -> [int]:
        """ Returns the ids of each DTO in the solution """
        return list(map(lambda dto_: dto_['id'], self.dtos))

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
        # Checks if the DTO would exceed the memory limit or if its AR is already served
        if self.ars_served[dto['ar_index']] \
                or self.get_tot_memory() + dto['memory'] > self.capacity:
            return False

        # Checks if the DTO is already in the plan
        index = binary_search(dto, self.dtos)
        if index != -1:
            return False

        # Checks if the DTO would overlap with another DTO
        for dto_ in self.dtos:
            if overlap(dto, dto_):
                return False
        return True

    def is_feasible(self, constraint: Constraint = None) -> bool:
        """ Checks if the solution is feasible or not.
            If constraint is given, it checks if the solution keeps the constraint,
            otherwise it checks all constraints. """
        if constraint is None:
            if not self.is_constraint_respected(Constraint.MEMORY):
                return False
            if not self.is_constraint_respected(Constraint.OVERLAP):
                return False
            if not self.is_constraint_respected(Constraint.SINGLE_SATISFACTION):
                return False
            if not self.is_constraint_respected(Constraint.DUPLICATES):
                return False

            return True
        else:
            if self.is_constraint_respected(constraint):
                return True
            else:
                return False

    def is_constraint_respected(self, constraint: Constraint) -> bool:
        """ Returns true if the solution respects the given constraint, false otherwise """
        if constraint == Constraint.MEMORY:
            if len(self.dlos) == 0:  # if problem is relaxed
                return self.get_tot_memory() < self.capacity
            else:  # if problem includes down-links
                dtos_copy = self.dtos.copy()
                memory: float = 0
                for dlo in self.dlos:
                    i: int = 0
                    while i < len(dtos_copy) and dlo['start_time'] > dtos_copy[i]['stop_time']:
                        memory += dtos_copy[i]['memory']
                        i += 1
                    dtos_copy = dtos_copy[i:]
                    if memory > self.capacity:
                        return False
                    for dto in dlo['downloaded_dtos']:
                        memory -= dto['memory']
                return True

        elif constraint == Constraint.OVERLAP:
            for index in range(self.size() - 1):
                if overlap(self.dtos[index], self.dtos[index + 1]):
                    return False
            return True

        elif constraint == Constraint.SINGLE_SATISFACTION:
            return len(self.get_ars_served()) == len(set(self.get_ars_served()))

        elif constraint == Constraint.DUPLICATES:
            return len(self.get_dto_ids()) == len(set(self.get_dto_ids()))

    def is_dto_downloaded(self, dto: DTO) -> bool:
        """ Returns true if the given DTO is downloaded in the solution """
        for dlo in self.dlos:
            index = binary_search(dto, dlo['downloaded_dtos'])
            if index != -1:
                return True
        return False

    def is_dto_downloadable(self, dto: DTO, dlo: DLO) -> bool:
        """ Returns true if the given DTO is downloaded in the solution """
        return sum(dto['memory'] for dto in dlo['downloaded_dtos']) + dto['memory'] <= \
            self.downlink_rate * (dlo['stop_time'] - dlo['start_time']) and \
            dto['stop_time'] < dlo['start_time'] and \
            not self.is_dto_downloaded(dto)

    def repair_memory(self):
        """ Repairs the memory constraint of the solution """
        # if len(self.dlos) == 0: # if problem is relaxed
        while not self.is_feasible(Constraint.MEMORY):
            index = np.random.randint(self.size())
            self.remove_dto_at(index)
        # else:  # if problem includes down-links
        #     for dlo in self.dlos:
        #         memory: float = 0
        #         current_index: int = 0
        #         while current_index < len(self.dtos) and dlo['start_time'] > self.dtos[current_index]['stop_time']:
        #             memory += self.dtos[current_index]['memory']
        #             current_index += 1
        #         if memory > self.capacity:
        #             return False

    def repair_overlap(self):
        """ Repairs the overlap constraint of the solution """
        while not self.is_feasible(Constraint.OVERLAP):
            i: int = 0
            while i < self.size() - 1:
                if overlap(self.dtos[i], self.dtos[i + 1]):
                    self.remove_dto_at(np.random.randint(i, i + 2))
                    i -= 1
                i += 1

    def repair_duplicates(self):
        """ Removes duplicate DTOs from the solution """
        new_dtos: [DTO] = []
        for dto in self.dtos:
            index = binary_search(dto, new_dtos)
            if index == -1:
                new_dtos.append(dto)
        self.dtos = new_dtos

    def repair_satisfaction(self):
        """ Repairs the single satisfaction constraint of the solution """
        ars_duplicate = [item for item, count in collections.Counter(self.get_ars_served()).items() if count > 1]

        for ar_id in ars_duplicate:
            index = np.where(np.array(self.get_ars_served()) == ar_id)[0][0]
            self.remove_dto_at(index)

    def plot_memory(self):
        """ Plots the memory of the solution """
        activities = self.dtos + self.dlos
        activities = sorted(activities, key=lambda activity_: activity_['start_time'])
        memories = []
        current_memory: float = 0
        for activity in activities:
            if 'ar_id' in activity:
                current_memory += activity['memory']
            else:
                for dto in activity['downloaded_dtos']:
                    current_memory -= dto['memory']
            memories.append(current_memory)

        x = np.arange(len(activities))
        plt.plot(x, memories, 'r-')
        plt.title('Memory')
        plt.show()

    def __str__(self) -> str:
        return f'Fitness: {self.fitness},\nFeasible: {self.is_feasible()},\nMemory occupied: {self.tot_memory},' \
               f'\nDTOs taken: {self.dtos[:5]}...,\nARs served: {self.ars_served[:5]}...'

    def update_downloaded_dtos(self):
        pass
        # shuffled_dtos: [DTO] = sample(self.dtos, len(self.dtos))
        # print(f'Duplicates? {len(shuffled_dtos) != len(list(set(shuffled_dtos)))}')
        # for dlo in self.dlos:
        #     for dto in shuffled_dtos:
        #         if self.is_dto_downloadable(dto, dlo):
        #             dlo['downloaded_dtos'].append(dto)
        #
        #     for dto in dlo['downloaded_dtos']:
        #         print(list(map(lambda x: x['id'], shuffled_dtos)))
        #         print(dto['id'])
        #         shuffled_dtos.remove(dto)
