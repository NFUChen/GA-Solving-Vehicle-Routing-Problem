from typing import Dict, List
from base_class import BuilderFactory

Solution = Dict[int,List[int]] # e.g.,  {0: [], 1: [0, 8, 6, 0], 2: [0, 7, 5, 0], 3: [0, 3, 0], 4: []}
class SolutionChromosome:
    pass
class SolutionChromosome(BuilderFactory):
    def __init__(self, solution:Solution, generation:int = 0) -> None:
        self.solution = solution
    
    def mutate(self, mutation_rate) -> SolutionChromosome:
        pass
        
        
        return self
    
    def crossover(self, _other_solution_chromosome:SolutionChromosome) -> List[SolutionChromosome]:
        pass
    
    def __repr__(self) -> str:
        return f"Chromosome: {self.solution}"
    
    def __eq__(self, _other_solution_chromosome:SolutionChromosome) -> bool:
        pass
    
    def __gt__(self, _other_solution_chromosome:SolutionChromosome) -> bool:
        pass
    
    @property
    def fitness(self):
        pass