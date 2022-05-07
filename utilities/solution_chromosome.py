from typing import Dict, List
from random import random, choice
from .base_class import BuilderFactory
from .route_resource_calculator import RouteResourceCalculator
from .mutation_strategy import MutationStrategy
# e.g.,  {0: [], 1: [0, 8, 6, 0], 2: [0, 7, 5, 0], 3: [0, 3, 0], 4: []}
Solution = Dict[int, List[int]]


class SolutionChromosome:
    pass


class SolutionChromosome(BuilderFactory):
    def __init__(self,
                 solution: Solution,
                 immutable_depot_names: List[int],
                 resources_used: Dict[str, float] = None,
                 generation: int = 0, ) -> None:
        self.solusion = solution
        # dont' choose vehicle without any depots being assigned, or len(route) < 3, [0,1,0] -> will cause mutation error,
        # mutation strategy need to pick two 'DIFFERENT' route index and that it shouldn't be 0
        self.vehicles_can_be_chosen = [vehicle
                                       for vehicle, route in self.solusion.items()
                                       if len(route) > 3]
        self.immutable_depot_names = immutable_depot_names
        self.mutation_strategy = MutationStrategy(immutable_depot_names)
        self.generation = generation
        self.resource_calc = RouteResourceCalculator()

        if resources_used is not None:
            self.resources_used = resources_used
            return

        self.resources_used = self.resource_calc.calculate_solution_resources(
            solution)

    def mutate(self, mutation_rate: float) -> SolutionChromosome:
        random_value = random()
        if random_value > mutation_rate:
            return self

        mutation_func = self.mutation_strategy.randomly_choose_mutation_strategy()

        chosen_vehicle_idx = self._randomly_choose_a_vehicle()
        chosen_vehicle_route = self.solusion[chosen_vehicle_idx]
        mutated_route = mutation_func(chosen_vehicle_route)

        # after mutation, update chromosome fitness ( based on self.resources_used, and self.solusion)
        self._update_resources_used(chosen_vehicle_idx, mutated_route)
        self.solusion[chosen_vehicle_idx] = mutated_route

        print("Mutate: ", mutation_func.__name__)
        print(chosen_vehicle_idx, chosen_vehicle_route)
        print(mutated_route)

        return self

    def crossover(self, _other_solution_chromosome: SolutionChromosome, crossover_rate: float) -> List[SolutionChromosome]:
        pass

    def __repr__(self) -> str:
        chromosome = f"Chromosome: {self.solusion}"
        resources = self.resources_used

        fuel_fee = f"Fuel Fee: ${int(resources['fuel_fee'])}"
        distance = f"Distance: {int(resources['distance'])} km"
        total_delivery_time = f"Total Delivery Time: {round(resources['delivery_time'] + resources['service_time'], 2)} Mins"
        vehicle_fixed_cost = f"Vehicle Fixed Cost: ${int(resources['vehicle_fixed_cost'])}"
        driver_cost = f"Driver Cost: ${int(resources['driver_cost'])}"
        total_cost_amount = int(
            resources['fuel_fee']) + resources['vehicle_fixed_cost'] + int(resources['driver_cost'])
        total_cost = f"Total Cost: ${total_cost_amount}"
        number_of_vehicles_assigned = f"Number of Vehicles Assigned: {resources['number_of_vehicles_assigned']}"
        number_of_replenishment = f"Number of Replenishsments: {resources['number_of_replenishment']}"
        sep = "-" * 60

        _repr = [
            chromosome,
            total_cost,
            fuel_fee,
            vehicle_fixed_cost,
            driver_cost,
            distance,
            total_delivery_time,
            number_of_vehicles_assigned,
            number_of_replenishment,
            sep
        ]

        return "\n\t".join(_repr)

    def __eq__(self, _other_solution_chromosome: SolutionChromosome) -> bool:
        return self.fitness == _other_solution_chromosome.fitness

    def __gt__(self, _other_solution_chromosome: SolutionChromosome) -> bool:
        # 總配送車數最小化為主要目標，
        # 降低總配送距離與減少每趟次的花費時間為次要目標，
        # 以求取最佳的配送路線。所以目標函數(1)為最小化車輛的固定成本、
        # 車輛行駛的距離成本、每趟次花費的司機員薪資成本。

        return self.fitness > _other_solution_chromosome.fitness

    @property
    def fitness(self) -> float:
        resources = self.resources_used
        total_cost = (
            resources["fuel_fee"] +
            resources["vehicle_fixed_cost"] +
            resources["driver_cost"]
        )
        return 1 / total_cost

    def _create_next_generation_self_with_new_solusion(self, new_solusion: Solution) -> SolutionChromosome:
        # passing in self.resources_used is for performance concern, which avoidss duplicate computation.
        return SolutionChromosome(new_solusion, self.immutable_depot_names, self.resources_used, self.generation + 1)

    def _randomly_choose_a_vehicle(self) -> int:

        return choice(self.vehicles_can_be_chosen)

    def _update_resources_used(self, vehicle_idx: int, updated_route: List[int]) -> None:
        '''
        After mutation, make sure we update chromosome 
        (e.g., self.resources_used, self.chromosome)
        '''

        original_route_resources = self.resource_calc.calculate_route_resources(
            vehicle_idx, self.solusion[vehicle_idx])
        updated_route_resources = self.resource_calc.calculate_route_resources(
            vehicle_idx, updated_route
        )

        for resource in self.resources_used.keys():
            self.resources_used[resource] -= original_route_resources[resource]
            self.resources_used[resource] += updated_route_resources[resource]
