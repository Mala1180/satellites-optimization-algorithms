import time

import matplotlib.pyplot as plt

from genetic import GeneticAlgorithm
from utils.functions import load_instance, overlap, add_dummy_dlo

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

    partial_results = []
    for i in range(10):
        print(f'Run Test Partial {i + 1}')
        start = time.time()
        ga = GeneticAlgorithm(CAPACITY, dtos, ars)
        ga.run()
        end = time.time()
        solution = ga.get_best_solution().fitness
        partial_results.append((solution, end - start))
        print(f'Run {i + 1} Result: {solution} in {end - start} seconds')


    plt.plot([result[0] for result in partial_results], label='Partial Problem')
    plt.legend()
    plt.show()

    INSTANCE = 'day1_40'
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

    complete_results = []
    for i in range(10):
        print(f'Run Test Complete {i + 1}')
        start = time.time()
        ga = GeneticAlgorithm(CAPACITY, dtos, ars, dlos, DOWNLINK_RATE)
        ga.run()
        end = time.time()
        solution = ga.get_best_solution().fitness
        complete_results.append((solution, end - start))
        print(f'Run {i + 1} Result: {solution} in {end - start} seconds')

    print(f'Partial Results: {partial_results}')
    print(f'Partial Average Result: {sum([result[0] for result in partial_results]) / len(partial_results)}')
    print(f'Partial Best Result: {max(partial_results, key=lambda result: result[0])}')

    print(f'Complete Results: {complete_results}')
    print(f'Complete Average Result: {sum([result[0] for result in complete_results]) / len(complete_results)}')
    print(f'Complete Best Result: {max(complete_results, key=lambda result: result[0])}')

    plt.plot([result[0] for result in partial_results], label='Partial Problem')
    plt.plot([result[0] for result in complete_results], label='Complete Problem')
    plt.legend()
    plt.show()

