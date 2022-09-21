from genetic import GeneticAlgorithm
from utils.functions import load_instance, overlap, add_dummy_dlo

if __name__ == '__main__':
    INSTANCE = 'test_large_complete'
    dtos, ars, constants, paws, dlos = load_instance(INSTANCE)

    initial_dlos = dlos

    # get rid of dtos overlapping with paws and dlos
    filtered_dtos = []
    for dto in dtos:
        skip = False
        for event in paws + dlos:
            if overlap(dto, event):
                skip = True
                break
        if not skip:
            filtered_dtos.append(dto)

    dtos = sorted(filtered_dtos, key=lambda dto_: dto_['start_time'])
    dlos = sorted(dlos, key=lambda dlo_: dlo_['start_time'])

    # add the dummy variable for the correct
    dlos = add_dummy_dlo(dtos, dlos)

    CAPACITY = constants['MEMORY_CAP']
    DOWNLINK_RATE = constants['DOWNLINK_RATE']

    for i, ar in enumerate(ars):
        ar['index'] = i

    for i, dto in enumerate(dtos):
        dto['priority'] = next((ar['rank'] for ar in ars if ar['id'] == dto['ar_id']), None)
        dto['ar_index'] = next((ar['index'] for ar in ars if ar['id'] == dto['ar_id']), None)

    ga = GeneticAlgorithm(CAPACITY, dtos, ars, dlos, DOWNLINK_RATE)
    ga.run()
    ga.print_population()
    ga.plot_fitness_values()

    solution = ga.get_best_solution()
    solution.plot_memory()

    print(f'Best solution: {solution}')
