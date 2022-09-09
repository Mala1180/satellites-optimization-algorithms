import collections
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
        self.dtos: [DTO] = [dto for dto in dtos]
        self.dtos = sorted(self.dtos, key=lambda dto_: dto_['start_time'])
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
            self.ars_served: ndarray = np.full(len(ars), False)
            for dto in self.dtos:
                self.ars_served[dto['ar_index']] = True
            # self.ars_served: ndarray = np.isin(self.ar_ids, [dto['ar_id'] for dto in self.dtos])

            # print("HERE ", np.all(self.ars_served_2 == self.ars_served))

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
        return True

    def add_and_download_dto(self, dto: DTO) -> bool:
        """ Adds a DTO to the solution and downloads it, returns True if the insertion and download were successful """
        if len(self.get_ars_served()) > self.ars_served.sum():
            print("POST ADD AND DOWNLOAD")
            print("len ar ids ", len(self.get_ars_served()))
            print("bool array len: ", self.ars_served.sum())

        if len(self.dlos) == 0:
            raise Exception("This method works only with downlink problems")

        # Checks if AR of the DTO is already served, and if DTO is already in the plan
        if self.ars_served[dto['ar_index']]:
            return False

        # Checks if the DTO would overlap with another DTO
        # TODO: it can be optimized by using find_insertion_point
        for dto_ in self.dtos:
            if overlap(dto, dto_):
                return False

        if not self.is_feasible():
            print("sono all'inizio", self.is_constraint_respected(Constraint.SINGLE_SATISFACTION))
            self.is_feasible()
            raise Exception("Plan is not feasible")

        for dlo in self.dlos:
            if len(list(map(lambda dto__: dto__['id'], dlo['downloaded_dtos']))) != len(
                    set(list(map(lambda dto__: dto__['id'], dlo['downloaded_dtos'])))):
                raise Exception("There are repeated DTOs in a DLO")

        if not self.is_feasible(Constraint.SINGLE_SATISFACTION):
            print(self.ars_served.sum())
            raise Exception("Single satisfaction constraint is not respected")

        self.add_dto(dto)
        if not self.is_feasible(Constraint.SINGLE_SATISFACTION):
            print("DOPO")
            print("len ar ids ", len(self.get_ars_served()))
            print("bool array len: ", self.ars_served.sum())
            raise Exception("Single satisfaction constraint is not respected")
        dlos_copy = self.dlos.copy()

        memory: float = 0
        added, downloaded, dlo_downloading_index = False, False, None
        success: bool = True
        i: int = 0
        j: int = 0
        # print("INIZIO")
        array_dtos_in = []

        for dlo in self.dlos:
            for dto_downloaded in dlo['downloaded_dtos']:
                if dto_downloaded not in self.dtos:
                    print("ERROR: DTO not in solution")
                    raise Exception("There is a downloaded DTO that is not in the solution")

        # print(sum([len(dlo['downloaded_dtos']) for dlo in self.dlos]), len(self.dtos))
        while i < len(self.dtos):
            # if the DTO comes before the DLO j, sum its memory
            if self.dtos[i]['stop_time'] < dlos_copy[j]['start_time']:
                # print(f'At dto {i}, memory is {memory + self.dtos[i]["memory"]} = {memory} + {self.dtos[i]["memory"]}')
                memory = memory + self.dtos[i]['memory']
                # print(f'Insert dto {self.dtos[i]["id"]}')
                array_dtos_in.append(self.dtos[i].copy())
                # if memory exceed because the new DTO is added, stop iterating and return False
                if memory > self.capacity:
                    success = False
                    break
                i += 1
            else:
                # the DLO j downloads all DTOs that were already there
                memory_downloaded: float = 0
                for dto_ in dlos_copy[j]['downloaded_dtos']:
                    # print(f'{memory} - {dto_["memory"]}')
                    memory = memory - dto_['memory']
                    # print(f'POP dto {dto_["id"]}')
                    if dto_ not in array_dtos_in:
                        print("ERROR")
                        raise Exception("The DLO is downloading a DTO that was not inserted")
                    array_dtos_in.remove(dto_)
                    memory_downloaded = memory_downloaded + dto_['memory']

                if memory < 0:
                    # print(f'Memory is negative: {memory}')
                    # print("Error at dlo index: ", j)
                    raise Exception('Memory is negative')

                # if the new DTO was added, if it can be downloaded during the DLO j, it is downloaded
                if not downloaded \
                        and dto['stop_time'] < dlos_copy[j]['start_time'] \
                        and self.is_dto_downloadable(dto, dlos_copy[j], memory_downloaded):
                    # print(f'{memory} - {dto["memory"]}')
                    memory = memory - dto['memory']
                    dlo_downloading_index = j
                    downloaded = True

                # print(f'At dlo {j}, memory is {memory}')

                j += 1

        # print("FINE")
        if success:
            if dlo_downloading_index is not None:
                self.dlos[dlo_downloading_index]['downloaded_dtos'].append(dto.copy())
        else:
            if downloaded:
                raise Exception("The DTO was downloaded but the solution is not feasible")
            self.remove_dto(dto.copy())

            for dlo in self.dlos:
                for dto_downloaded in dlo['downloaded_dtos']:
                    if dto_downloaded not in self.dtos:
                        raise Exception("There is a downloaded DTO that is not in the solution")

        if not self.is_feasible():
            print(f' MEMORY: {self.is_feasible(Constraint.MEMORY)},'
                  f' OVERLAP: {self.is_feasible(Constraint.OVERLAP)},'
                  f' SINGLE_SATISFACTION: {self.is_feasible(Constraint.SINGLE_SATISFACTION)},'
                  f' DUPLICATES: {self.is_feasible(Constraint.DUPLICATES)}')
            raise Exception("Plan is not feasible")

        for dlo in self.dlos:
            for dto_downloaded in dlo['downloaded_dtos']:
                if dto_downloaded not in self.dtos:
                    raise Exception("There is a downloaded DTO that is not in the solution")
            if len(list(map(lambda dto__: dto__['id'], dlo['downloaded_dtos']))) != len(
                    set(list(map(lambda dto__: dto__['id'], dlo['downloaded_dtos'])))):
                raise Exception("There are repeated DTOs in a DLO")

        if len(self.get_ars_served()) > self.ars_served.sum():
            print("POST ADD AND DOWNLOAD")
            print("len ar ids ", len(self.get_ars_served()))
            print("bool array len: ", self.ars_served.sum())
            raise Exception("ERROR: ARs served is not correct")

        return success

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

        same_ar_dtos = [dto_ for dto_ in self.dtos.copy() if dto_['ar_index'] == dto['ar_index']]
        # if there aren't other dtos of the same AR, the AR is not served anymore
        if len(same_ar_dtos) == 0:
            self.ars_served[dto['ar_index']] = False

        for dlo in self.dlos:
            if dto in dlo['downloaded_dtos']:
                dlo['downloaded_dtos'].remove(dto)

    def keeps_feasibility(self, dto: DTO) -> bool:
        """ Returns True if the solution keeps feasibility if the DTO would be added """
        # if len(self.dtos) > 0:
        #     raise Exception("This method works only with relaxed problems")

        # Checks if the DTO would exceed the memory limit
        if self.get_tot_memory() + dto['memory'] > self.capacity:
            return False

        # Checks if AR of the DTO is already served, and if DTO is already in the plan
        if self.ars_served[dto['ar_index']]:
            return False

        # Checks if the DTO would overlap with another DTO
        # TODO: it can be optimized by using find_insertion_point
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
                memory: float = 0
                i: int = 0
                j: int = 0
                while i < len(self.dtos):
                    # if the DTO comes before the DLO j, sum its memory
                    if self.dtos[i]['stop_time'] < self.dlos[j]['start_time']:
                        memory = memory + self.dtos[i]['memory']
                        # print(f'At dto {i}, memory is {memory}')
                        # if memory exceed because the new DTO is added, stop iterating and return False
                        if memory > self.capacity:
                            # print(f"Memory exceeded: {memory} at dto: {i} before dlo: {j}")
                            return False
                        i += 1
                    else:
                        for dto in self.dlos[j]['downloaded_dtos']:
                            memory = memory - dto['memory']
                        # print(f'After dlo {j}, memory is {memory}')

                        if memory < 0:
                            # print(f"Memory exceeded in negative: {memory} at dlo: {j}")
                            return False
                        j += 1

                return True

                # dtos_copy = self.dtos.copy()
                # memory: float = 0
                # for dlo in self.dlos.copy():
                #     i: int = 0
                #     while i < len(dtos_copy) and dlo['start_time'] > dtos_copy[i]['stop_time']:
                #         memory = memory + dtos_copy[i]['memory']
                #         print(f'At dto {i}, memory is {memory}')
                #         i += 1
                #     dtos_copy = dtos_copy[i:]
                #     if memory > self.capacity:
                #         print(f"Memory exceeded: {memory} at dlo index: {self.dlos.index(dlo)} and dto index: {i - 1}")
                #         return False
                #     for dto in dlo['downloaded_dtos']:
                #         memory = memory - dto['memory']
                #     print(f'At dlo {self.dlos.index(dlo)}, memory is {memory}')
                #
                #     if memory < 0:
                #         return False
                # return True

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

        for ar_id in ars_duplicate:
            index = np.where(np.array(self.get_ars_served()) == ar_id)[0][0]
            self.remove_dto_at(index)

        if len(self.get_ars_served()) > self.ars_served.sum():
            print("len ar ids ", len(self.get_ars_served()))
            print("bool array len: ", self.ars_served.sum())
            raise Exception("Repair satisfaction failed")

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

    def update_downloaded_dtos(self):
        memory: float = 0
        downloadable_dtos: [DTO] = []

        for dlo in self.dlos:
            dlo['downloaded_dtos'] = []

        if not self.is_constraint_respected(Constraint.DUPLICATES):
            raise Exception('The solution contains duplicates')

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
                if self.is_dto_downloaded(dto):
                    raise Exception('The DTO is already downloaded')

                if self.is_dto_downloadable(dto, dlo, memory_downloaded):
                    dlo['downloaded_dtos'].append(dto.copy())
                    memory = memory - dto['memory']
                    if memory < 0:
                        raise Exception('Memory is negative')
                    memory_downloaded += dto['memory']
                    downloadable_dtos.remove(dto)
                    i -= 1
                i += 1

        for dlo in self.dlos:
            if len(list(map(lambda dto__: dto__['id'], dlo['downloaded_dtos']))) != len(
                    set(list(map(lambda dto__: dto__['id'], dlo['downloaded_dtos'])))):
                raise Exception("There are repeated DTOs in a DLO")

    def __str__(self) -> str:
        return f'Fitness: {self.fitness},\nFeasible: {self.is_feasible()},\nMemory occupied: {self.tot_memory},' \
               f'\nDTOs taken: {self.dtos[:5]}...,\nARs served: {self.ars_served[:5]}...'
