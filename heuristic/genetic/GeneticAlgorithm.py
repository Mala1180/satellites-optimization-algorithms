import matplotlib.pyplot as plt
import numpy as np
from typing import List
from random import randrange
from heuristic.genetic.Chromosome import Chromosome
from heuristic.genetic.vars import DTO


class GeneticAlgorithm:
    """ Implements the structure and methods of a genetic algorithm to solve satellite optimization problem """

    def __init__(self, capacity, total_dtos, num_generations=10, num_chromosomes=5, num_elites=2) -> None:
        """ Creates a random initial population """
        self.total_dtos: [DTO] = total_dtos
        self.num_generations: int = num_generations
        self.num_elites: int = num_elites
        self.elites: [Chromosome] = []
        self.fitness_history: [float] = []
        self.population: [Chromosome] = []
        self.population_fitness: [float] = []
        self.population_tot_fitness: float = 0

        for i in range(num_chromosomes):
            memory: float = 0
            chromosome = Chromosome()
            while memory < capacity:
                index: int = randrange(len(total_dtos))
                dto_to_insert: DTO = self.total_dtos[index]
                chromosome.add_dto(dto_to_insert)
                memory += dto_to_insert['memory']
            self.population.append(chromosome)

        self.update_population_fitness()

    @staticmethod
    def fitness(chromosome: Chromosome) -> float:
        """ Calculates and returns the fitness value of a single chromosome """
        fitness_value: float = 0
        for dto in chromosome.dtos:
            fitness_value += dto['priority']
        return fitness_value

    def update_population_fitness(self):
        """ Calculates and update the fitness value of the entire population """
        self.population_tot_fitness = 0
        for chromosome in self.population:
            fitness_value = self.fitness(chromosome)
            self.population_fitness.append(fitness_value)
            self.population_tot_fitness += fitness_value

    def elitism(self):
        """ Defines the elites for the current generation """
        self.elites = []
        for _ in range(self.num_elites):
            elite = max(self.population, key=lambda chromosome: chromosome.get_tot_priority())
            self.elites.append(elite)

    def parent_selection(self) -> [Chromosome]:
        """ Chooses and returns the chromosomes to make crossover with """
        parents: [Chromosome] = []
        num_best_chromosome = 2  # len(self.population) / 5
        for _ in range(num_best_chromosome):
            parent_index = randrange(len(self.population))
            parents.append(parents[parent_index])

        return parents

    def crossover(self):
        pass

    def mutation(self):
        pass

    def create_new_population(self, new_chromosomes: List[Chromosome]):
        """ Replace some chromosomes of new population with the newer ones """
        num_worst_chromosome = 2
        for i in range(num_worst_chromosome):
            min(self.population_fitness)

    def run(self):
        for i in range(self.num_generations):
            print(f'Generation {i + 1}')
            self.update_population_fitness()
            self.fitness_history.append(self.population_tot_fitness)
            print(f'Fitness: {self.population_tot_fitness}')
            self.elitism()

    def print_population(self):
        print(f'Population : [')
        for chromosome in self.population:
            print(f'   ({chromosome.dtos},')
            print(f'    - Memory occupied: {chromosome.get_tot_memory()},')
            print(f'    - Total priority: {chromosome.get_tot_priority()})')

        print(']')

    def plot_fitness_values(self):
        plt.plot(np.arange(0, self.num_generations), self.fitness_history)
        plt.title('Fitness values - Generations')
        plt.show()
