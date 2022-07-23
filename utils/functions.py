def overlap(event1, event2):
    """ Returns True if events overlap, False otherwise """
    return event1['start_time'] <= event2['stop_time'] and event1['stop_time'] >= event2['start_time']


def binary_search(dto, plan, low, high) -> int:
    """ Recursive implementation of binary search.
        Returns index of dto in the given chromosome, -1 if not found """
    if high >= low:
        mid = (high + low) // 2

        # If element is present at the middle itself
        if plan[mid] == dto:
            return mid

        # If element is smaller than mid, then it can only be present in left sub-array
        elif plan[mid]['start_time'] > dto['start_time']:
            return binary_search(dto, plan, low, mid - 1)

        # Else the element can only be present in right sub-array
        else:
            return binary_search(dto, plan, mid + 1, high)

    else:
        # Element is not present in the array
        return -1


def find_insertion_point(dto, plan, low, high) -> int:
    """ Finds the insertion index for a dto in the plan """
    mid = (high + low) // 2

    if plan[mid]['start_time'] <= dto['start_time'] < plan[mid + 1]['start_time']:
        return mid + 1

    elif plan[mid]['start_time'] > dto['start_time']:
        return binary_search(dto, plan, low, mid - 1)
    else:
        return binary_search(dto, plan, mid + 1, high)