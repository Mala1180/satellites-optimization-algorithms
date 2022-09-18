from genetic import GeneticAlgorithm
from utils.functions import load_instance, overlap


if __name__ == '__main__':
    dtos, ars, constants, paws = load_instance('day1_0')[:4]

    # get rid of dtos overlapping with paws
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

    CAPACITY: float = constants['MEMORY_CAP']
    DTOS_NUMBER: int = len(dtos)

    for i, ar in enumerate(ars):
        ar['index'] = i

    for i, dto in enumerate(dtos):
        dto['priority'] = next((ar['rank'] for ar in ars if ar['id'] == dto['ar_id']), None)
        dto['ar_index'] = next((ar['index'] for ar in ars if ar['id'] == dto['ar_id']), None)

    ga = GeneticAlgorithm(CAPACITY, dtos, ars)
    ga.run()
    ga.print_population()
    ga.plot_fitness_values()

    solution = ga.get_best_solution()
    solution.plot_memory()

    print(f'Best solution: {solution}')
