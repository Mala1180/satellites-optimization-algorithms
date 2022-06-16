from random import randrange, uniform, sample

import matplotlib.pyplot as plt
import numpy as np

from heuristic.genetic.Chromosome import Chromosome
from heuristic.genetic.vars import DTO


class GeneticAlgorithm:
    """ Implements the structure and methods of a genetic algorithm to solve satellite optimization problem """

    def __init__(self, capacity, total_dtos, num_generations=10, num_chromosomes=5, num_elites=2) -> None:
        """ Creates a random initial population and does preliminary stuffs """
        self.total_dtos: [DTO] = total_dtos
        self.num_generations: int = num_generations
        self.num_elites: int = num_elites
        self.elites: [Chromosome] = []
        self.parents: [(Chromosome, Chromosome)] = []
        self.fitness_history: [float] = []
        self.population: [Chromosome] = []
        self.population_fitness: [float] = []
        self.population_tot_fitness: float = 0

        for i in range(num_chromosomes):
            memory: float = 0
            chromosome = Chromosome()

            while memory < capacity:
                index: int = randrange(len(total_dtos))
                dto_to_insert: DTO = total_dtos[index]
                if dto_to_insert not in chromosome.dtos:
                    chromosome.add_dto(dto_to_insert)
                    memory += dto_to_insert['memory']

            self.population.append(chromosome)

    @staticmethod
    def fitness(dto: DTO, min_priority: float, max_priority: float) -> float:
        """ Calculates and returns the fitness value of a single DTO """
        # fitness_value: float = 0
        # return dto['priority']
        return (dto['priority'] - min_priority) / (max_priority - min_priority)

    def update_chromosome_fitness(self, chromosome: Chromosome):
        """ Updates the fitness value of a chromosome and of each dto """
        fitness_value: float = 0
        for dto in chromosome.dtos:
            dto_fitness = self.fitness(dto, chromosome.get_min_priority(), chromosome.get_max_priority())
            fitness_value += dto_fitness
            dto['fitness'] = dto_fitness
        chromosome.fitness = fitness_value

    def update_population_fitness(self):
        """ Updates the fitness value of the entire population """
        self.population_tot_fitness = 0
        self.population_fitness = []

        for chromosome in self.population:
            self.update_chromosome_fitness(chromosome)
            self.population_fitness.append(chromosome.fitness)
            self.population_tot_fitness += chromosome.fitness

    def elitism(self):
        """ Defines the elites for the current generation """
        self.elites = []
        for _ in range(self.num_elites):
            elite = max(self.population, key=lambda chromosome: chromosome.fitness)
            self.elites.append(elite)

    def parent_selection(self) -> [Chromosome]:
        """ Chooses and returns the chromosomes to make crossover with roulette wheel selection method """
        self.parents = []

        # finds number of couples equals to population length - elites length
        for i in range(len(self.population) - len(self.elites)):
            # random number for roulette pick
            pick: float = uniform(0, self.population_tot_fitness)
            current: float = 0
            # random chromosome to instantiate the first parent variable
            parent1: Chromosome = self.population[randrange(0, len(self.population))]

            # picks the first parent with roulette wheel method
            for index, chromosome in enumerate(self.population):
                current += chromosome.fitness / self.population_tot_fitness
                if current > pick:
                    parent1 = chromosome
                    break

            # picks the second parent randomly within the population
            parent2 = self.population[randrange(0, len(self.population))]
            self.parents.append((parent1, parent2))

    def crossover(self):
        """ Makes crossover between each couple of parents, and replaces the entire population except
            elites with the new offspring """

        sons: [Chromosome] = []
        for parent1, parent2 in self.parents:
            rand1, rand2 = sample(range(0, len(parent1.dtos)), 2)
            i1, i2 = (rand1, rand2) if rand1 <= rand2 else (rand2, rand1)
            son_dtos = parent1.dtos[:i1] + parent2.dtos[i1:i2] + parent1.dtos[i2:]
            sons.append(Chromosome(son_dtos))

        self.population = self.elites + sons

    def mutation(self):
        pass

    def run(self):
        for i in range(self.num_generations):
            print(f'Generation {i + 1}')
            self.update_population_fitness()
            self.fitness_history.append(self.population_tot_fitness)
            print(f'Fitness: {self.population_tot_fitness}')
            self.elitism()
            self.parent_selection()
            self.crossover()

    def get_best_solution(self) -> Chromosome:
        return max(self.population, key=lambda chromosome: chromosome.fitness)

    def print_population(self):
        print(f'Population : [')
        for chromosome in self.population:
            print(f'   ({chromosome.dtos},')
            print(f'    - Memory occupied: {chromosome.get_tot_memory()},')
            print(f'    - Total priority: {chromosome.get_tot_priority()})')

        print(']')
        print(f'Number of chromosomes: {len(self.population)}')

    def plot_fitness_values(self):
        plt.plot(np.arange(0, self.num_generations), self.fitness_history)
        plt.title('Fitness values - Generations')
        plt.show()
