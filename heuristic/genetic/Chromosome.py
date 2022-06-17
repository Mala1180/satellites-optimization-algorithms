import numpy as np
from heuristic.genetic.vars import DTO, AR


class Chromosome:
    """ A class that represents a possible solution of GeneticAlgorithm class """

    def __init__(self, dtos: [DTO] = None) -> None:
        """ If no argument is given, creates an empty solution, otherwise a solution with given DTOs  """
        if dtos is None:
            dtos = []
        self.dtos: [DTO] = sorted(dtos, key=lambda dto_: dto_['start_time'])
        self.tot_fitness: float = sum(self.get_priorities())
        self.tot_memory: float = sum(self.get_memories())
        self.ars_served = np.array([dto_['ar_id'] for dto_ in self.dtos])

    def __str__(self) -> str:
        return f'Fitness: {self.tot_fitness},\nMemory occupied: {self.tot_memory},' \
               f'\nDTOs taken: {self.dtos},\nARs served: {self.ars_served}'

    def print(self) -> None:
        print(self)

    def size(self) -> int:
        return len(self.dtos)

    def add_dto(self, dto: DTO) -> bool:
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
        np.append(self.ars_served, dto['ar_id'])
        return True

    def remove_dto(self, dto: DTO) -> bool:
        if len(self.dtos) == 0 or not np.isin(dto, self.dtos):
            return False
        index = np.searchsorted(self.dtos, dto)
        self.dtos = np.delete(self.dtos, index)
        self.tot_memory -= dto['memory']
        self.tot_fitness -= dto['priority']
        np.delete(self.ars_served, np.where(self.ars_served == dto['ar_id']))
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

    @staticmethod
    def overlap(event1: DTO, event2: DTO):
        return event1['start_time'] <= event2['stop_time'] and event1['stop_time'] >= event2['start_time']
