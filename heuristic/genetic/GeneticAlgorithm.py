from random import sample

import matplotlib.pyplot as plt
import numpy as np

from heuristic.genetic.Chromosome import Chromosome
from heuristic.genetic.vars import DTO, AR


class GeneticAlgorithm:
    """ Implements the structure and methods of a genetic algorithm to solve satellite optimization problem """

    def __init__(self, capacity, total_dtos, num_generations=10, num_chromosomes=5) -> None:
        """ Creates a random initial population and does preliminary stuffs """
        self.capacity = capacity
        print(f'Capacity: {capacity}')
        self.total_dtos: [DTO] = total_dtos
        # self.ars: [AR] = ars
        self.num_generations: int = num_generations
        self.elite: Chromosome = Chromosome()
        self.parents: [(Chromosome, Chromosome)] = []
        self.fitness_history: [float] = []
        self.population: [Chromosome] = []

        for i in range(num_chromosomes):
            memory: float = 0
            chromosome = Chromosome()

            shuffled_dtos: [DTO] = sample(self.total_dtos, len(self.total_dtos))
            for dto in shuffled_dtos:
                if chromosome.size() == 0 or \
                        (not np.isin(dto['ar_id'], chromosome.get_ars_served())
                         and memory + dto['memory'] <= self.capacity):
                    if chromosome.add_dto(dto):
                        memory += dto['memory']

            self.population.append(chromosome)

    def elitism(self):
        """ Updates the elite for the current generation """
        self.elite = max(self.population, key=lambda chromosome: chromosome.get_tot_fitness())

    def parent_selection(self) -> [Chromosome]:
        """ Chooses and returns the chromosomes to make crossover with roulette wheel selection method """
        self.parents = []

        # finds number of couples equals to population length - elites length
        for i in range(len(self.population) - 1):
            # picks the first parent based on fitness (roulette wheel method)
            population_tot_fitness = sum([chromosome.get_tot_fitness() for chromosome in self.population])
            selection_probs = [chromosome.get_tot_fitness() / population_tot_fitness
                               for chromosome in self.population]
            parent1 = self.population[np.random.choice(len(self.population), p=selection_probs)]

            # picks the second parent randomly within the population
            parent2 = self.population[np.random.randint(len(self.population))]
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

        self.population = [self.elite] + sons

    def mutation(self):
        pass

    def run(self):
        for i in range(self.num_generations):
            print(f'Generation {i + 1}')
            chromosome_fitness = [chromosome.get_tot_fitness() for chromosome in self.population]
            self.fitness_history.append(chromosome_fitness)
            print(f'Fitness: {self.fitness_history[i]}')
            self.elitism()
            self.parent_selection()
            self.crossover()

    def get_best_solution(self) -> Chromosome:
        return max(self.population, key=lambda chromosome: chromosome.get_tot_fitness())

    def is_solution_feasible(self, chromosome: Chromosome) -> bool:
        """ Checks if a solution is feasible or not """
        # memory constraint check
        if chromosome.get_tot_memory() > self.capacity:
            return False

        # overlap constraint check
        for dto1 in chromosome.dtos:
            for dto2 in chromosome.dtos:
                if chromosome.overlap(dto1, dto2):
                    return False

        # single satisfaction check
        if len(np.unique(chromosome.get_ars_served())) != len(chromosome.get_ars_served()):
            return False
        return True

    def print_population(self):
        print(f'Population : [')
        for chromosome in self.population:
            print(f'   ({chromosome.dtos},')
            print(f'    - Memory occupied: {chromosome.get_tot_memory()},')
            print(f'    - Total priority: {chromosome.get_tot_fitness()})')
            print(f'    - Feasible: {self.is_solution_feasible(chromosome)})')

        print(']')
        print(f'Number of chromosomes: {len(self.population)}')

    def plot_fitness_values(self):
        history = np.array(self.fitness_history)
        for i in range(len(history[0, :])):
            plt.plot(np.arange(0, self.num_generations), history[:, i])
        plt.title('Fitness values - Generations')
        plt.show()
