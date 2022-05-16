from typing import List, TypeVar

from heuristic.genetic.Gene import Gene

Event = TypeVar("Event")


class Chromosome:
    """ A linked list of Genes """

    def __init__(self) -> None:
        self.head_gene = None
        self.length = 0

    def print(self) -> None:
        gene = self.head_gene
        while gene is not None:
            print(f' -> {gene.print()}')
            gene = gene.next

    def count(self) -> int:
        return self.length

    def head_insert(self, gene: Gene) -> None:
        self.length += 1
        new_gene = Gene(gene.id, gene.start_time, gene.stop_time, gene.memory)
        new_gene.next = self.head_gene
        self.head_gene = new_gene

    def tail_insert(self, gene: Gene) -> None:
        self.length += 1
        new_gene = Gene(gene.id, gene.start_time, gene.stop_time, gene.memory)
        if self.head_gene is None:
            self.head_gene = new_gene
            return

        gene = self.headval
        while gene.nextval is not None:
            gene = gene.nextval
        gene.next = new_gene

    def index_insert(self, gene: Gene, index: int) -> bool:
        new_gene = Gene(gene.id, gene.start_time, gene.stop_time, gene.memory)
        if index > self.count() - 1 or index < 0:
            return False
        self.length += self.length + 1

    @staticmethod
    def overlap(event1: Event, event2: Event):
        return event1['start_time'] <= event2['stop_time'] and event1['stop_time'] >= event2['start_time']
