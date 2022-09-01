from random import sample, choice

import matplotlib.pyplot as plt
import numpy as np

from utils import Constraint
from . import Chromosome
from .crossover import MultiPointCrossover
from .crossover import SinglePointCrossover
from .crossover import TimeFeasibleCrossover

from .my_types import DTO
from .parent_selection import RouletteWheelSelection


class GeneticAlgorithm:
    """ Implements the structure and methods of a genetic algorithm to solve satellite optimization problem """

    def __init__(self, capacity, total_dtos, total_ars, num_generations=300, num_chromosomes=30,
                 crossover_strategy='time'):
        """ Creates a random initial population and prepares data for the algorithm """
        if crossover_strategy == 'single':
            self.crossover_strategy = SinglePointCrossover()
        elif crossover_strategy == 'multi':
            self.crossover_strategy = MultiPointCrossover()
        elif crossover_strategy == 'time':
            self.crossover_strategy = TimeFeasibleCrossover()
        else:
            raise ValueError(f'Invalid crossover strategy: {crossover_strategy}, choose from "single" or "multi"')
        self.capacity = capacity
        print(f'Capacity: {capacity}')
        self.total_dtos: [DTO] = total_dtos
        self.total_ars: [DTO] = total_ars
        self.ordered_dtos = sorted(total_dtos, key=lambda dto_: dto_['priority'], reverse=True)
        self.num_generations: int = num_generations
        self.elites: [Chromosome] = []
        self.parents: [(Chromosome, Chromosome)] = []
        self.fitness_history: [float] = []
        self.population: [Chromosome] = []

        for i in range(num_chromosomes):
            chromosome = Chromosome(self.capacity, total_ars)
            shuffled_dtos: [DTO] = sample(self.total_dtos, len(self.total_dtos))

            for dto in shuffled_dtos:
                if chromosome.size() == 0 or chromosome.keeps_feasibility(dto):
                    chromosome.add_dto(dto)

            self.population.append(chromosome)

    def elitism(self):
        """ Updates the elites for the current generation """
        self.elites = sorted(self.population, key=lambda chromosome: chromosome.get_tot_fitness(), reverse=True)[:3]
        # self.elite = max(self.population, key=lambda chromosome: chromosome.get_tot_fitness())

    def parent_selection(self) -> [Chromosome]:
        """ Chooses and returns the chromosomes to make crossover with roulette wheel selection method """
        self.parents = []
        parent_selection_strategy = RouletteWheelSelection(self.population)
        # finds number of couples equals to population length - elites length
        for i in range(len(self.population) - len(self.elites)):
            parents: (Chromosome, Chromosome) = parent_selection_strategy.select(self.population)
            self.parents.append(parents)

    def crossover(self):
        """ Makes crossover between each couple of parents, and replaces the entire population except
            elites with the new offspring """
        sons: [Chromosome] = []
        for parent1, parent2 in self.parents:
            son_dtos = self.crossover_strategy.crossover(parent1, parent2)
            sons.append(Chromosome(self.capacity, self.total_ars, son_dtos))

        self.population = self.elites + sons

    def mutation(self):
        """ Mutates randomly the 10% of each chromosome in the population """
        for chromosome in list(set(self.population) - set(self.elites)):
            # Inserts 10 random DTOs in the plan
            # for _ in range(10):
            #     new_dto = choice(self.total_dtos)
            #     # chromosome.remove_dto_at(np.random.randint(0, len(chromosome.dtos)))
            #     chromosome.add_dto(new_dto)

            # Replaces 10% of DTOs in the plan with new random DTOs
            for _ in range(len(chromosome.dtos) // 10):
                new_dto = choice(self.total_dtos)

                # if chromosome.keeps_feasibility(new_dto):
                # chromosome.remove_dto_at(np.random.randint(0, len(chromosome.dtos)))
                chromosome.add_dto(new_dto)

    def repair(self):
        """ Repairs the population if some chromosomes are not feasible """
        for chromosome in self.population:
            if not chromosome.is_feasible(Constraint.OVERLAP):
                chromosome.repair_overlap()
            if not chromosome.is_feasible(Constraint.SINGLE_SATISFACTION):
                chromosome.repair_satisfaction()
            if not chromosome.is_feasible(Constraint.MEMORY):
                chromosome.repair_memory()
            if not chromosome.is_feasible(Constraint.DUPLICATES):
                chromosome.repair_duplicates()

    def local_search(self):
        """ Performs local search on the population. Tries to insert new DTOs in the plan. """
        for chromosome in self.population:
            for dto in self.ordered_dtos:
                if chromosome.keeps_feasibility(dto):
                    chromosome.add_dto(dto)

    def run(self):
        """ Starts the algorithm itself """
        for i in range(self.num_generations):
            print(f'Generation {i + 1}')
            self.elitism()
            self.parent_selection()
            self.crossover()
            self.mutation()
            self.repair()
            self.local_search()
            chromosome_fitness = [chromosome.get_tot_fitness() for chromosome in self.population]
            self.fitness_history.append(chromosome_fitness)
            print(f'Fitness: {self.fitness_history[i]}')

    def get_best_solution(self) -> Chromosome:
        """ Returns the best solution in the population after running of the algorithm """
        return max(self.population, key=lambda chromosome: chromosome.get_tot_fitness())

    def print_population(self):
        """ Prints all solutions and the relative info """
        print(f'Population : [')
        for chromosome in self.population:
            print(f'   Len: {len(chromosome.dtos)}, ({chromosome.dtos},')
            print(f'    - Memory occupied: {chromosome.get_tot_memory()},')
            print(f'    - Total priority: {chromosome.get_tot_fitness()}')
            print(f'    - Feasibility: [MEMORY: {chromosome.is_feasible(Constraint.MEMORY)},'
                  f' OVERLAP: {chromosome.is_feasible(Constraint.OVERLAP)},'
                  f' SINGLE_SATISFACTION: {chromosome.is_feasible(Constraint.SINGLE_SATISFACTION)},'
                  f' DUPLICATES: {chromosome.is_feasible(Constraint.DUPLICATES)}])')

        print(']')
        print(f'Number of chromosomes: {len(self.population)}')

    def plot_fitness_values(self):
        """ Plots how the fitness of each solution changes over the generations """
        history = np.array(self.fitness_history)
        for i in range(len(history[0, :])):
            plt.plot(np.arange(0, self.num_generations), history[:, i])
        plt.title('Fitness values - Generations')
        plt.show()
