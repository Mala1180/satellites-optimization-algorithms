import collections

from copy import deepcopy
from typing import Optional

import numpy as np
from matplotlib import pyplot as plt
from random import sample

from utils import Constraint
from utils.functions import overlap, binary_search, find_insertion_point
from .my_types import DTO, AR, DLO, DEBUG


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
        self.dtos: [DTO] = deepcopy(dtos)
        self.dtos = sorted(self.dtos, key=lambda dto_: dto_['start_time'])
        # Loads ARs
        self.ars: [AR] = deepcopy(ars)
        # Loads DLOs
        self.dlos: [DLO] = []
        if tot_dlos is not None:
            self.dlos = deepcopy(tot_dlos)

        self.dlos = sorted(self.dlos, key=lambda dlo_: dlo_['start_time'])

        if len(self.dtos) == 0:
            self.ar_ids_served: [int] = []
            self.ars_served = np.full(len(ars), False)
        else:
            self.ar_ids_served: [int] = [dto['ar_id'] for dto in self.dtos]
            self.ars_served = np.isin(list(map(lambda ar: ar['id'], self.ars)),
                                      self.ar_ids_served)

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

    def get_fitness(self) -> float:
        """ Returns the fitness of the solution """
        return self.fitness

    def get_ars_served(self) -> [int]:
        """ Returns the ARs ids satisfied by the solution """
        # return list(map(lambda dto: dto['ar_id'], self.dtos))
        return self.ar_ids_served

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

    def add_dto(self, dto: DTO) -> bool:
        """ Adds a DTO to the solution in start time order, updates total memory, fitness and ARs served.
            Returns True if the insertion """
        if self.ars_served[dto['ar_index']]:
            return False

        index = find_insertion_point(dto, self.dtos)
        self.dtos.insert(index, dto)
        self.tot_memory += dto['memory']
        self.fitness += dto['priority']
        self.ars_served[dto['ar_index']] = True
        self.ar_ids_served.append(dto['ar_id'])
        return True

    def add_and_download_dto(self, dto: DTO) -> bool:
        """ Tries to add and download a DTO to the solution,
        returns True if the insertion is successful """
        if len(self.dlos) == 0:
            raise Exception("This method works only with downlink problems")

        # Checks if AR of the DTO is already served, and if DTO is already in the plan
        if self.ars_served[dto['ar_index']]:
            return False

        # Checks if the DTO would overlap with another DTO
        insertion_index = find_insertion_point(dto, self.dtos)
        if insertion_index == 0:
            if overlap(dto, self.dtos[0]):
                return False
        elif insertion_index == len(self.dtos):
            if overlap(dto, self.dtos[-1]):
                return False
        else:
            if overlap(dto, self.dtos[insertion_index - 1]) or overlap(dto, self.dtos[insertion_index]):
                return False

        backup_dlos = deepcopy(self.dlos)
        self.add_dto(dto)

        memory: float = 0
        added = False
        success: bool = True
        dtos_in_memory: [DTO] = []
        i: int = 0
        j: int = 0
        while i < len(self.dtos) and success:
            # if the DTO comes before the DLO j, sum its memory
            if self.dtos[i]['stop_time'] < self.dlos[j]['start_time']:
                memory = memory + self.dtos[i]['memory']
                dtos_in_memory.append(self.dtos[i].copy())
                if dto == self.dtos[i]:
                    added = True
                # if memory exceed because the new DTO is added, stop iterating and return False
                if memory > self.capacity:
                    success = False
                i += 1
            else:
                # the DLO j downloads all DTOs that were already there
                memory_downloaded: float = 0
                if not added:
                    for dto_ in self.dlos[j]['downloaded_dtos']:
                        memory -= dto_['memory']
                        memory_downloaded += dto_['memory']
                        dtos_in_memory.remove(dto_)
                else:
                    self.dlos[j]['downloaded_dtos'] = []
                    dtos_in_memory.sort(key=lambda dto__: dto__['memory'], reverse=True)
                    z: int = 0
                    while z < len(dtos_in_memory):
                        if self.is_dto_downloadable(dtos_in_memory[z], self.dlos[j], memory_downloaded):
                            self.dlos[j]['downloaded_dtos'].append(dtos_in_memory[z].copy())
                            memory -= dtos_in_memory[z]['memory']
                            memory_downloaded += dtos_in_memory[z]['memory']
                            dtos_in_memory.remove(dtos_in_memory[z].copy())
                            z -= 1
                        z += 1
                j += 1

        if not success:
            self.remove_dto(dto)
            self.dlos = backup_dlos

        if DEBUG and not self.is_feasible():
            raise Exception("Plan is not feasible")

        return success

    def remove_dto(self, dto: DTO) -> bool:
        """ Removes a DTO from the solution """
        index = binary_search(dto, self.dtos)
        if index == -1:
            return False
        return self.remove_dto_at(index)

    def remove_dto_at(self, index: int):
        """ Removes the DTO at the given index, raises an exception if the index is out of bounds """
        if index < 0 or index >= len(self.dtos):
            print(f'Index:{index}, len(self.dtos):{len(self.dtos)}')
            raise IndexError("Index out of range")
        dto = self.dtos[index]
        self.ar_ids_served.remove(dto['ar_id'])
        self.dtos.pop(index)
        self.tot_memory -= dto['memory']
        self.fitness -= dto['priority']

        if dto['ar_id'] not in self.ar_ids_served:
            self.ars_served[dto['ar_index']] = False

        for dlo in self.dlos:
            if dto in dlo['downloaded_dtos']:
                dlo['downloaded_dtos'].remove(dto)

    def keeps_feasibility(self, dto: DTO) -> bool:
        """ Returns True if the solution keeps feasibility if the DTO would be added """
        # Checks if the DTO would exceed the memory limit
        if self.get_tot_memory() + dto['memory'] > self.capacity:
            return False

        # Checks if AR of the DTO is already served, and if DTO is already in the plan
        if self.ars_served[dto['ar_index']]:
            return False

        # Checks if the DTO would overlap with another DTO
        index = find_insertion_point(dto, self.dtos)
        if index == 0:
            if overlap(dto, self.dtos[0]):
                return False
        elif index == len(self.dtos):
            if overlap(dto, self.dtos[-1]):
                return False
        else:
            if overlap(dto, self.dtos[index - 1]) or overlap(dto, self.dtos[index]):
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
                memory: float = 0
                i: int = 0
                j: int = 0

                while i < len(self.dtos):
                    # if the DTO comes before the DLO j, sum its memory
                    if self.dtos[i]['stop_time'] < self.dlos[j]['start_time']:
                        memory = memory + self.dtos[i]['memory']
                        # if memory exceed because the new DTO is added, stop iterating and return False
                        if memory > self.capacity:
                            return False
                        i += 1
                    else:
                        for dto in self.dlos[j]['downloaded_dtos']:
                            memory = memory - dto['memory']

                        if memory < 0:
                            return False
                        j += 1

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

    def is_dto_downloadable(self, dto: DTO, dlo: DLO, memory_downloaded: float) -> bool:
        """ Returns true if the given DTO is downloaded in the solution """
        if dto['stop_time'] >= dlo['start_time']:
            raise Exception('The DTO comes after the DLO')
        return memory_downloaded + dto['memory'] <= self.downlink_rate * (dlo['stop_time'] - dlo['start_time'])

    def repair_memory(self):
        """ Repairs the memory constraint of the solution """
        if len(self.dlos) == 0:  # if problem is relaxed
            while not self.is_feasible(Constraint.MEMORY):
                index = np.random.randint(self.size())
                self.remove_dto_at(index)
            return True
        else:  # if problem includes down-links
            dtos_copy = self.dtos.copy()
            memory: float = 0
            for dlo in self.dlos:
                i: int = 0
                start_index = i
                while i < len(dtos_copy) and dlo['start_time'] > dtos_copy[i]['stop_time']:
                    memory = memory + dtos_copy[i]['memory']
                    i += 1

                restart = False
                while memory > self.capacity:
                    index = np.random.randint(start_index, i)
                    memory = memory - dtos_copy[index]['memory']
                    self.remove_dto(dtos_copy[index])
                    dtos_copy.pop(index)
                    i -= 1
                    restart = True
                if restart:
                    return False

                for dto in dlo['downloaded_dtos']:
                    memory = memory - dto['memory']

                dtos_copy = dtos_copy[i:]

            return True

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

        # for each AR that is served more than once, removes extra DTOs
        for ar_id in ars_duplicate:
            dtos_same_ar = [dto for dto in self.dtos if dto['ar_id'] == ar_id]
            # removes the DTOs with same AR, except one
            for dto in sample(dtos_same_ar, len(dtos_same_ar) - 1):
                self.remove_dto(dto)

    def update_downloaded_dtos(self):
        memory: float = 0
        downloadable_dtos: [DTO] = []

        for dlo in self.dlos:
            dlo['downloaded_dtos'] = []

        for j, dlo in enumerate(self.dlos):
            if j == 0:
                dtos_between_dlos: [DTO] = self.get_dtos_between_dates(0, dlo['start_time'])
            else:
                dtos_between_dlos: [DTO] = self.get_dtos_between_dates(self.dlos[j - 1]['stop_time'], dlo['start_time'])

            memory = memory + sum(list(map(lambda dto_: dto_['memory'], dtos_between_dlos)))
            downloadable_dtos += dtos_between_dlos
            downloadable_dtos.sort(key=lambda dto_: dto_['memory'], reverse=True)
            memory_downloaded: float = 0
            i: int = 0
            while i < len(downloadable_dtos):
                dto = downloadable_dtos[i]
                if DEBUG and self.is_dto_downloaded(dto):
                    raise Exception('The DTO is already downloaded')

                if self.is_dto_downloadable(dto, dlo, memory_downloaded):
                    dlo['downloaded_dtos'].append(dto.copy())
                    memory = memory - dto['memory']
                    memory_downloaded += dto['memory']
                    downloadable_dtos.remove(dto)
                    i -= 1
                i += 1

    def plot_memory(self):
        """ Shows the memory trend of the solution on a graph """
        activities = self.dtos + self.dlos
        activities = sorted(activities, key=lambda activity_: activity_['start_time'])
        memories = [0]
        current_memory: float = 0
        for activity in activities:
            if 'ar_id' in activity:
                current_memory = current_memory + activity['memory']
            else:
                for dto in activity['downloaded_dtos']:
                    current_memory = current_memory - dto['memory']
            memories.append(current_memory)

        x = np.arange(len(activities) + 1)
        plt.plot(x, memories, 'r-')
        plt.title('Memory')
        plt.show()

    def __str__(self) -> str:
        return f'Fitness: {self.fitness},\nFeasible: {self.is_feasible()},\nMemory occupied: {self.tot_memory},' \
               f'\nDTOs taken: {self.dtos[:5]}...,\nARs served: {self.ars_served[:5]}...'
