from random import sample, choice, choices

import matplotlib.pyplot as plt
import numpy as np

from heuristic.genetic.Chromosome import Chromosome
from heuristic.genetic.vars import DTO
from utils.Constraint import Constraint


class GeneticAlgorithm:
    """ Implements the structure and methods of a genetic algorithm to solve satellite optimization problem """

    def __init__(self, capacity, total_dtos, total_ars, num_generations=150, num_chromosomes=20):
        """ Creates a random initial population and prepares data for the algorithm """
        self.capacity = capacity
        print(f'Capacity: {capacity}')
        self.total_dtos: [DTO] = total_dtos
        self.total_ars: [DTO] = total_ars
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

        # finds number of couples equals to population length - elites length
        for i in range(len(self.population) - len(self.elites)):
            # picks the first parent based on fitness (roulette wheel method)
            population_tot_fitness = sum([chromosome.get_tot_fitness() for chromosome in self.population])
            selection_probs = [chromosome.get_tot_fitness() / population_tot_fitness
                               for chromosome in self.population]
            parent1 = choices(self.population, weights=selection_probs, k=1)[0]

            # picks the second parent randomly within the population
            parent2 = self.population[np.random.randint(len(self.population))]
            self.parents.append((parent1, parent2))

    def crossover(self):
        """ Makes crossover between each couple of parents, and replaces the entire population except
            elites with the new offspring """

        sons: [Chromosome] = []
        for parent1, parent2 in self.parents:
            # multi point crossover
            # rand1, rand2 = sample(range(0, len(parent1.dtos)), 2)
            # i1, i2 = (rand1, rand2) if rand1 <= rand2 else (rand2, rand1)
            # son_dtos = parent1.dtos[:i1] + parent2.dtos[i1:i2] + parent1.dtos[i2:]

            index = np.random.randint(0, len(parent1.dtos))
            son_dtos = parent1.dtos[:index] + parent2.dtos[index:]

            sons.append(Chromosome(self.capacity, self.total_ars, son_dtos))

        print(f"CROSSOVER, len elites: {len(self.elites)}, len sons: {len(sons)}")
        self.population = self.elites + sons

    def mutation(self):
        """ Mutates randomly the 10% of each chromosome in the population """
        for chromosome in self.population:
            for _ in range(10):
                new_dto = choice(self.total_dtos)
                chromosome.add_dto(new_dto)
            # for _ in range(len(chromosome.dtos) // 10):
            #     new_dto = choice(self.total_dtos)
            #
            #     if chromosome.keeps_feasibility(new_dto):
            #         chromosome.remove_dto_at(np.random.randint(0, len(chromosome.dtos)))
            #         chromosome.add_dto(new_dto)

    def repair(self):
        """ Repairs the population if some chromosomes are not feasible """
        for chromosome in self.population:
            if not chromosome.is_feasible(Constraint.OVERLAP):
                chromosome.repair_overlap()
            if not chromosome.is_feasible(Constraint.SINGLE_SATISFACTION):
                chromosome.repair_satisfaction()
            if not chromosome.is_feasible(Constraint.MEMORY):
                chromosome.repair_memory()

    def run(self):
        """ Starts the algorithm itself """
        for i in range(self.num_generations):
            print(f'Generation {i + 1}')
            self.elitism()
            self.parent_selection()
            self.crossover()
            self.mutation()
            self.repair()
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
            print(f'   ({chromosome.dtos},')
            print(f'    - Memory occupied: {chromosome.get_tot_memory()},')
            print(f'    - Total priority: {chromosome.get_tot_fitness()}')
            print(f'    - Feasibility: [MEMORY: {chromosome.is_feasible(Constraint.MEMORY)},'
                  f' OVERLAP: {chromosome.is_feasible(Constraint.OVERLAP)},'
                  f' SINGLE_SATISFACTION: {chromosome.is_feasible(Constraint.SINGLE_SATISFACTION)})]')

        print(']')
        print(f'Number of chromosomes: {len(self.population)}')

    def plot_fitness_values(self):
        """ Plots how the fitness of each solution changes over the generations """
        history = np.array(self.fitness_history)
        for i in range(len(history[0, :])):
            plt.plot(np.arange(0, self.num_generations), history[:, i])
        plt.title('Fitness values - Generations')
        plt.show()
