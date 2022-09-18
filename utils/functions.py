import json
import os


def load_instance(instance: str) -> tuple:
    """ Loads the instance from the file. Returns a tuple containing DTOs, ARs, constants, PAWs, DLOs """
    # read JSON files
    root_dir = os.path.dirname(__file__)
    print(root_dir)
    dtos_file = open(f'{root_dir}/../instances/{instance}/DTOs.json')
    ars_file = open(f'{root_dir}/../instances/{instance}/ARs.json')
    constants_file = open(f'{root_dir}/../instances/{instance}/constants.json')
    paws_file = open(f'{root_dir}/../instances/{instance}/PAWs.json')
    dlos_file = open(f'{root_dir}/../instances/{instance}/DLOs.json')

    # loads JSON, the result is a dictionary
    dtos = json.loads(dtos_file.read())
    ars = json.loads(ars_file.read())
    constants = json.loads(constants_file.read())
    paws = json.loads(paws_file.read())
    dlos = json.loads(dlos_file.read())
    return dtos, ars, constants, paws, dlos


def overlap(event1, event2):
    """ Returns True if events overlap, False otherwise """
    return event1['start_time'] <= event2['stop_time'] and event1['stop_time'] >= event2['start_time']


def add_dummy_dlo(dtos, dlos):
    """
    Adds the dummy variable for some next constraints

    :param dtos: list of dtos
    :param dlos: list of dlos
    :return: dlos with dummy dlo added
    """
    ordered_dtos = sorted(dtos, key=lambda dto_: dto_['start_time'])
    ordered_dlos = sorted(dlos, key=lambda dlo_: dlo_['start_time'])
    stop_time = max(ordered_dtos[-1]['stop_time'], ordered_dlos[-1]['stop_time'])
    dummy_dlo = ordered_dlos[-1].copy()
    dummy_dlo['start_time'] = stop_time + 1
    dummy_dlo['stop_time'] = dummy_dlo['start_time']
    ordered_dlos.append(dummy_dlo)
    return ordered_dlos


def binary_search(dto, plan) -> int:
    """ Iterative implementation of binary search.
        Returns index of dto in the given plan, -1 if not found """
    low = 0
    high = len(plan) - 1
    while high >= low:
        mid = (high + low) // 2

        # If element is present at the middle itself
        if plan[mid] == dto:
            return mid

        # If element is smaller than mid, then it can only be present in left sub-array
        if dto['start_time'] > plan[mid]['start_time']:
            low = mid + 1

        # Else the element can only be present in right sub-array
        else:
            high = mid - 1

    # Element is not present in the array
    return -1


def find_insertion_point(dto, plan) -> int:
    """ Finds the insertion index for a dto in the plan """
    if len(plan) == 0 or dto['start_time'] <= plan[0]['start_time']:
        return 0
    if dto['start_time'] >= plan[-1]['start_time']:
        return len(plan)

    low = 0
    high = len(plan) - 1
    while high >= low:
        mid = low + (high - low) // 2

        if plan[mid]['start_time'] <= dto['start_time'] <= plan[mid + 1]['start_time']:
            return mid + 1

        if dto['start_time'] > plan[mid]['start_time']:
            low = mid + 1
        else:
            high = mid - 1
