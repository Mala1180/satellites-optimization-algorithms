from typing import TypeVar
import matplotlib.pyplot as plt
import numpy as np
from heuristic.genetic.Chromosome import Chromosome
from random import randrange


class GeneticAlgorithm:
    """ Implements the structure and methods of a genetic algorithm to solve satellite optimization problem """

    def __init__(self, capacity, total_dtos, num_generations=10, num_chromosomes=5) -> None:
        self.total_dtos = total_dtos
        self.num_generations = num_generations
        self.fitness_values = []
        self.population = []
        for i in range(num_chromosomes):
            memory = 0
            chromosome = Chromosome()
            while memory < capacity:
                index = randrange(len(total_dtos))
                dto_to_insert = total_dtos[index]
                chromosome.add_dto(dto_to_insert)
                memory += dto_to_insert['memory']
            self.population.append(chromosome)

    def fitness(self):
        pass

    def crossover(self):
        pass

    def mutation(self):
        pass

    def run(self):
        for i in range(self.num_generations):
            print(f'Generation {i + 1}')

    def print_population(self):
        print(f'Population : [')
        for chromosome in self.population:
            print(f'   ({chromosome.dtos},')
            print(f'    - Memory occupied: {chromosome.get_tot_memory()},')
            print(f'    - Total priority: {chromosome.get_tot_priority()})')

        print(']')

    def plot_fitness_values(self):
        plt.plot(np.arange(0, self.num_generations), self.fitness_values)
        plt.title('Fitness values - Generations')
        plt.show()
