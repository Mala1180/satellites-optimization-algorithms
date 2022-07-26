from utils.functions import load_instance, overlap

from genetic import GeneticAlgorithm

dtos, ars, constants, paws = load_instance('day1_0')[:4]

# get rid of dtos overlapping with paws and dlos
filtered_dtos = []
for dto in dtos:
    skip = False
    for event in paws:
        if overlap(dto, event):
            skip = True
            break
    if not skip:
        filtered_dtos.append(dto)

dtos = filtered_dtos

memories = list(map(lambda dto_: dto_['memory'], dtos))
priorities = []

CAPACITY: float = constants['MEMORY_CAP']
DTOS_NUMBER: int = len(dtos)

for i, ar in enumerate(ars):
    ar['index'] = i

# populate array of priorities
for i, dto in enumerate(dtos):
    priorities.append(next((ar['rank'] for ar in ars if ar['id'] == dto['ar_id']), None))
    dto['priority'] = priorities[i]
    dto['ar_index'] = next((ar['index'] for ar in ars if ar['id'] == dto['ar_id']), None)

ga = GeneticAlgorithm(CAPACITY, dtos, ars)
ga.run()
ga.print_population()
ga.plot_fitness_values()

solution = ga.get_best_solution()
solution.plot_memory()

print(f'Best solution: {solution}')
