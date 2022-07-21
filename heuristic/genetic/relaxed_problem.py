import json

from heuristic.genetic.GeneticAlgorithm import GeneticAlgorithm

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

ga = GeneticAlgorithm(CAPACITY, dtos)
ga.run()
ga.print_population()
ga.plot_fitness_values()

solution = ga.get_best_solution()

print(f'Best solution: {solution}')

# if solution.is_feasible():
#     prova_dto = max(dtos, key=lambda dto_: dto_["start_time"])
#     print('Last dto taken:', solution.get_last_dto()['start_time'])
#     print('Prova dto :', prova_dto['start_time'])
#     print(f'KEEPS {solution.keeps_feasibility(prova_dto)}')

print(f'UGUALI? \n {sorted(solution.dtos, key=lambda dto: dto["start_time"]) == solution.dtos}')
