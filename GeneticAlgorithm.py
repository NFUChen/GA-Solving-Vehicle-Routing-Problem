class Gene:
    def __init__(self, depot) -> None:
        '''
        a gene is a depot
        '''

        self.depot = depot


    


class Chromosome:
    def __init__(self, genes:Gene) -> None:
        '''
        Chromosome represents a possible solutions
        '''
        self.genes = genes

class GeneticAlgorithm:
    def __init__(self, population_size, 
                       mutation_rate,mutation_interval, 
                       crossover_rate, crossover_interval,
                       iteration) -> None:
        pass

    def _generate_initial_population(self) -> None:
        pass

    def _calculate_fitness_value(self) -> None:
        pass

    def _selection(self) -> None:
        pass

    def _crossover(self) -> None:
        pass

    def _mutation(self) -> None:
        pass


    @property
    def is_termination_criteria_met(self) -> bool:

        return False

    def run(self) -> None:
        initial_population = self._generate_initial_population()
        while not (self.is_termination_criteria_met):
            self._calculate_fitness_value()
            self._selection()
            self._crossover()
            self._mutation()
        
        


        







# dataset_name ,9
# num_of_node ,8
# num_of_car ,3
# u ,20
# Tk ,480
# r ,168
# iteration ,1000
# num_of_population ,1000
# mutation_rate ,0.4
# crossover_rate ,0.6
# updata_fig_frequency ,2