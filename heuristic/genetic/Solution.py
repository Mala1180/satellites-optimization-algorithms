from typing import List, TypeVar

Event = TypeVar("Event")


class Solution:

    def __init__(self) -> None:
        self.dtos: List = []

    def create_population(self, quantity: int) -> None:
        pass

    def add_dto(self) -> None:
        pass

    def remove_dto(self) -> None:
        pass

    def order_population(self) -> None:
        self.dtos = sorted(self.dtos, key=lambda dto: dto['start_time'])


    @staticmethod
    def overlap(event1: Event, event2: Event):
        return event1['start_time'] <= event2['stop_time'] and event1['stop_time'] >= event2['start_time']


