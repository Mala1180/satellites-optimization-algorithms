def overlap(event1, event2):
    return event1['start_time'] <= event2['stop_time'] and event1['stop_time'] >= event2['start_time']
