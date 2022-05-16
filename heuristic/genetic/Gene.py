from typing import TypeVar

timestamp = TypeVar('timestamp')


class Gene:

    def __init__(self, id_: int, start_time: timestamp, stop_time: timestamp, memory: timestamp) -> None:
        self.id = id_
        self.start_time = start_time
        self.stop_time = stop_time
        self.memory = memory

        self.next = None

    def print(self) -> None:
        print(f'Id: {self.id}, Start: {self.start_time}, Stop: {self.stop_time}, Memory: {self.memory}')
