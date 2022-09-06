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
                 tot_dlos: [DLO] = None, downlink_rate: float = None) -> None:
        """ If no argument is given, creates an empty solution, otherwise creates a solution with given DTOs """
        if dtos is None:
            dtos = []
        if tot_dlos is None:
            tot_dlos = []
        # Loads DTOs
        self.dtos: [DTO] = []
        for dto in dtos:
            self.dtos.append(dto)
        self.dtos = sorted(self.dtos, key=lambda dto_: dto_['start_time'])
        for dto in self.dtos:
            dto['memory'] = round(dto['memory'], 2)
        # Loads ARs
        self.ars: [AR] = [ar for ar in ars]
        self.ar_ids: [int] = list(map(lambda ar: ar['id'], self.ars))
        # Loads DLOs
        self.dlos: [DLO] = []
        for j in range(len(tot_dlos)):
            dlo = tot_dlos[j].copy()
            dlo['downloaded_dtos'] = []
            self.dlos.append(dlo)

        self.dlos = sorted(self.dlos, key=lambda dlo_: dlo_['start_time'])

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
                return False
            else:
                index = find_insertion_point(dto, self.dtos)

        self.dtos.insert(index, dto)
        dto['memory'] = round(dto['memory'], 2)
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
        self.tot_memory -= round(dto['memory'], 2)
        self.fitness -= dto['priority']
        self.ars_served[dto['ar_index']] = False

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

    def get_dtos_before_dlo(self, dlo: DLO):
        """ Returns the DTOs that comes before the given DLO """
        return [dto for dto in self.dtos if dto['stop_time'] < dlo['start_time']]

    def get_dtos_between_dates(self, start_time: float, stop_time: float):
        """ Returns the DTOs between the given interval """
        return [dto for dto in self.dtos if dto['start_time'] > start_time and dto['stop_time'] < stop_time]

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
                        memory = round(memory + dtos_copy[i]['memory'], 2)
                        i += 1
                    dtos_copy = dtos_copy[i:]
                    if memory > self.capacity:
                        return False
                    for dto in dlo['downloaded_dtos']:
                        memory = round(memory - dto['memory'], 2)

                    if memory < 0:
                        return False
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
            # try:
            #     index1 = dlo['downloaded_dtos'].index(dto)
            # except ValueError:
            #     index1 = -1
            # print(f'index:{index}, index1:{index1}, uguali? {index == index1}')
            if index != -1:
                return True
        return False

    def is_dto_downloadable(self, dto: DTO, dlo: DLO, current_memory: float) -> bool:
        """ Returns true if the given DTO is downloaded in the solution """
        memory_downloaded = sum(round(dto['memory'], 2) for dto in dlo['downloaded_dtos']) + dto['memory']
        return memory_downloaded <= self.downlink_rate * (dlo['stop_time'] - dlo['start_time']) and \
            dto['stop_time'] < dlo['start_time'] and \
            round(current_memory - dto['memory'], 2) >= 0 and \
            not self.is_dto_downloaded(dto)

    def repair_memory(self):
        """ Repairs the memory constraint of the solution """
        if len(self.dlos) == 0:  # if problem is relaxed
            while not self.is_feasible(Constraint.MEMORY):
                index = np.random.randint(self.size())
                self.remove_dto_at(index)
        else:  # if problem includes down-links
            dtos_copy = self.dtos.copy()
            memory: float = 0
            for dlo in self.dlos:
                i: int = 0
                start_index = i
                while i < len(dtos_copy) and dlo['start_time'] > dtos_copy[i]['stop_time']:
                    memory = round(memory + dtos_copy[i]['memory'], 2)
                    i += 1
                while memory > self.capacity:
                    index = np.random.randint(start_index, i)
                    memory = round(memory - dtos_copy[index]['memory'], 2)
                    if dtos_copy[index] in dlo['downloaded_dtos']:
                        dlo['downloaded_dtos'].remove(dtos_copy[index])
                    self.remove_dto(dtos_copy[index])
                    dtos_copy.pop(index)
                    i -= 1
                for dto in dlo['downloaded_dtos']:
                    memory = round(memory - dto['memory'], 2)

                dtos_copy = dtos_copy[i:]

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
        memories = [0]
        current_memory: float = 0
        for activity in activities:
            if 'ar_id' in activity:
                current_memory = round(current_memory + activity['memory'], 2)
            else:
                for dto in activity['downloaded_dtos']:
                    current_memory = round(current_memory - dto['memory'], 2)
            memories.append(current_memory)

        x = np.arange(len(activities) + 1)
        plt.plot(x, memories, 'r-')
        plt.title('Memory')
        plt.show()

    def update_downloaded_dtos(self):
        memory: float = 0
        downloaded_dtos: [DTO] = []
        for j, dlo in enumerate(self.dlos):
            if j == 0:
                dtos_between_dlos: [DTO] = self.get_dtos_between_dates(0, dlo['start_time'])
            else:
                dtos_between_dlos: [DTO] = self.get_dtos_between_dates(self.dlos[j - 1]['stop_time'], dlo['start_time'])

            memory = round(memory + round(sum(list(map(lambda dto: dto['memory'], dtos_between_dlos))), 2), 2)

            downloadable_dtos: [DTO] = [dto for dto in self.get_dtos_before_dlo(dlo)
                                        if dto not in downloaded_dtos]
            # print(sum(dto['memory'] for dto in downloadable_dtos))
            # print(memory)
            downloadable_dtos = sample(downloadable_dtos, len(downloadable_dtos))
            for dto in downloadable_dtos:
                if round(memory - dto['memory'], 2) < 0:
                    print("here")
                if self.is_dto_downloadable(dto, dlo, memory):
                    dlo['downloaded_dtos'].append(dto.copy())
                    memory = round(memory - dto['memory'], 2)
                    downloadable_dtos.remove(dto)

            downloaded_dtos.extend(dlo['downloaded_dtos'].copy())
            # print(memory)

    # self.plot_memory()

    # if not self.is_constraint_respected(Constraint.MEMORY):
    #     # self.plot_memory()
    #     print('Memory constraint not respected')
    #     print(self.is_constraint_respected(Constraint.MEMORY))

    def __str__(self) -> str:
        return f'Fitness: {self.fitness},\nFeasible: {self.is_feasible()},\nMemory occupied: {self.tot_memory},' \
               f'\nDTOs taken: {self.dtos[:5]}...,\nARs served: {self.ars_served[:5]}...'
