from random import sample, choice

import matplotlib.pyplot as plt
import numpy as np

from utils import Constraint
from . import Chromosome
from .crossover import MultiPointCrossover
from .crossover import SinglePointCrossover
from .crossover import TimeFeasibleCrossover

from .my_types import DTO, DLO, DEBUG
from .parent_selection import RouletteWheelSelection


class GeneticAlgorithm:
    """ Implements the structure and methods of a genetic algorithm to solve satellite optimization problem """

    def __init__(self, capacity, total_dtos, total_ars, total_dlos=None, downlink_rate=None,
                 num_generations=150, num_chromosomes=20, num_elites=3, crossover_strategy='time_feasible'):
        """ Creates a random initial population and prepares data for the algorithm """
        if crossover_strategy == 'single':
            self.crossover_strategy = SinglePointCrossover()
        elif crossover_strategy == 'multi':
            self.crossover_strategy = MultiPointCrossover()
        elif crossover_strategy == 'time_feasible':
            self.crossover_strategy = TimeFeasibleCrossover()
        else:
            raise ValueError(f'Invalid crossover strategy: {crossover_strategy}, choose from "single" or "multi"')
        self.capacity = capacity
        self.downlink_rate = downlink_rate
        self.num_elites = num_elites
        print(f'Capacity: {capacity}')
        self.total_dtos: [DTO] = total_dtos.copy()
        for dto in self.total_dtos:
            dto['memory']: int = round(dto['memory'])
        self.total_ars: [DTO] = total_ars.copy()
        self.total_dlos: [DLO] = []
        if total_dlos is not None:
            self.total_dlos = total_dlos.copy()

        self.ordered_dtos = sorted(total_dtos, key=lambda dto_: dto_['priority'], reverse=True)
        self.num_generations: int = num_generations
        self.elites: [Chromosome] = []
        self.parents: [(Chromosome, Chromosome)] = []
        self.fitness_history: [float] = []
        self.population: [Chromosome] = []

        for i in range(num_chromosomes):
            chromosome = Chromosome(self.capacity, total_ars.copy(),
                                    tot_dlos=self.total_dlos.copy(),
                                    downlink_rate=self.downlink_rate)
            shuffled_dtos: [DTO] = sample(self.total_dtos, len(self.total_dtos))

            for dto in shuffled_dtos:
                if chromosome.size() == 0 or chromosome.keeps_feasibility(dto):
                    chromosome.add_dto(dto)

            self.population.append(chromosome)

    def elitism(self):
        """ Updates the elites for the current generation """
        self.elites = sorted(self.population,
                             key=lambda chromosome: chromosome.get_tot_fitness(),
                             reverse=True)[: self.num_elites]

    def parent_selection(self):
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
            son = Chromosome(self.capacity, self.total_ars.copy(), son_dtos.copy(),
                             self.total_dlos.copy(), self.downlink_rate)
            sons.append(son)
            if DEBUG and not son.is_constraint_respected(Constraint.DUPLICATES):
                raise Exception('The solution contains duplicates')

        self.population = self.elites + sons

    def mutation(self):
        """ Mutates randomly the 10% of each chromosome in the population """
        for chromosome in list(set(self.population) - set(self.elites)):
            # Replaces 10% of DTOs in the plan with new random DTOs
            for _ in range(len(chromosome.dtos) // 10):
                new_dto = choice(self.total_dtos)
                chromosome.add_dto(new_dto)

    def repair(self):
        """ Repairs the population if some chromosomes are not feasible """
        for chromosome in self.population:
            if not chromosome.is_feasible(Constraint.OVERLAP):
                chromosome.repair_overlap()
            if not chromosome.is_feasible(Constraint.SINGLE_SATISFACTION):
                chromosome.repair_satisfaction()
                if DEBUG and not chromosome.is_feasible(Constraint.SINGLE_SATISFACTION):
                    raise Exception('Constraint violated')
            if not chromosome.is_feasible(Constraint.DUPLICATES):
                chromosome.repair_duplicates()
            if not chromosome.is_feasible(Constraint.MEMORY):
                while not chromosome.repair_memory():
                    chromosome.update_downloaded_dtos()
            for dlo in chromosome.dlos:
                if DEBUG and len(list(map(lambda dto__: dto__['id'], dlo['downloaded_dtos']))) != len(
                        set(list(map(lambda dto__: dto__['id'], dlo['downloaded_dtos'])))):
                    raise Exception("There are repeated DTOs in a DLO")

    def local_search(self):
        """ Performs local search on the population. Tries to insert new DTOs in the plan. """
        for chromosome in list(set(self.population) - set(self.elites)):
            for dto in self.ordered_dtos[:len(self.ordered_dtos) // 5]:
                if len(self.total_dlos) == 0:
                    if chromosome.keeps_feasibility(dto):
                        chromosome.add_dto(dto)
                else:
                    chromosome.add_and_download_dto(dto)
                    if DEBUG and len(chromosome.get_ars_served()) > chromosome.ars_served.sum():
                        print("len ar ids ", len(chromosome.get_ars_served()))
                        print("bool array len: ", chromosome.ars_served.sum())
                        raise Exception("There are repeated ARs in the plan")

            # chromosome.update_downloaded_dtos()

    def run(self):
        """ Starts the algorithm itself """
        for i in range(self.num_generations):
            print(f'Generation {i + 1}')
            self.elitism()
            self.parent_selection()
            self.crossover()
            self.mutation()
            if len(self.total_dlos) > 0:
                self.update_downloaded_dtos()
            self.repair()
            self.local_search()
            chromosome_fitness = [chromosome.get_tot_fitness() for chromosome in self.population]
            self.fitness_history.append(chromosome_fitness)
            print(f'Fitness: {self.fitness_history[i]}')

    def update_downloaded_dtos(self):
        for chromosome in list(set(self.population) - set(self.elites)):
            chromosome.update_downloaded_dtos()

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
            print(f'    - Feasible: [MEMORY: {chromosome.is_feasible(Constraint.MEMORY)},'
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
