import json
import numpy as np
from heuristic.genetic.Chromosome import Chromosome
from typing import List

from heuristic.genetic.GeneticAlgorithm import GeneticAlgorithm
from utils.overlap import overlap

INSTANCE = 'day1_0'

# read JSON files

dtos_file = open(f'../../data/{INSTANCE}/DTOs.json')
ars_file = open(f'../../data/{INSTANCE}/ARs.json')
constants_file = open(f'../../data/{INSTANCE}/constants.json')
paws_file = open(f'../../data/{INSTANCE}/PAWs.json')

# loads JSON, the result is a dictionary
dtos = json.loads(dtos_file.read())
ars = json.loads(ars_file.read())
constants = json.loads(constants_file.read())
paws = json.loads(paws_file.read())

memories = list(map(lambda dto_: dto_['memory'], dtos))
priorities = []

CAPACITY: float = constants['MEMORY_CAP']
DTOS_NUMBER: int = len(dtos)

# populate array of priorities
for index_dto, dto in enumerate(dtos):
    priorities.append(next((ar['rank'] for ar in ars if ar['id'] == dto['ar_id']), None))
    dto['priority'] = priorities[index_dto]


def fitness(solution: List[int], solution_index: int) -> float:
    mask = np.where(solution == 1, True, False)
    solution_memories = np.where(solution == 1, memories, 0)
    fitness_value: float = 0

    if np.sum(solution_memories) > CAPACITY:
        fitness_value = fitness_value - 5 * (CAPACITY - np.sum(solution_memories))

    for i1, dto1 in enumerate(dtos):
        # if the dto1 is in the plan
        if solution[i1] == 1:

            # overlap with paws constraint
            for paw in paws:
                if overlap(dto1, paw):
                    fitness_value = fitness_value - 50

            # overlap with other dtos constraint
            for i2, dto2 in enumerate(dtos):
                # if the dto1 is in the plan
                if solution[i2] == 1:
                    if overlap(dto1, dto2) and dto1 != dto2:
                        fitness_value = fitness_value - 20

    fitness_value = fitness_value + np.sum(np.where(solution == 1, priorities, 0))
    return fitness_value


ga = GeneticAlgorithm(CAPACITY, dtos)
ga.print_population()

# ga = pygad.GA(num_generations=10,
#               num_parents_mating=2,
#               fitness_func=fitness,
#               num_genes=DTOS_NUMBER,
#               gene_space=[0, 1],
#               gene_type=int,
#               parent_selection_type='sss',
#               initial_population=initial_population)
