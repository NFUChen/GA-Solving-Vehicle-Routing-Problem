from typing import Dict, List
from random import random
from .base_class import BuilderFactory
from .route_resource_calculator import RouteResourceCalculator
from .mutation_strategy import MutationStrategy
# e.g.,  {0: [], 1: [0, 8, 6, 0], 2: [0, 7, 5, 0], 3: [0, 3, 0], 4: []}
Solution = Dict[int, List[int]]


class SolutionChromosome:
    pass


class SolutionChromosome(BuilderFactory):
    def __init__(self, solution: Solution, immutable_depot_names: List[int], generation: int = 0) -> None:
        self.chromosome = solution
        self.immutable_depot_names = immutable_depot_names
        self.generation = generation

        self.resource_calc = RouteResourceCalculator()
        self.each_route_resource = [].copy()
        self.resources_used = self._calculate_solution_resources(
            solution)

        self.number_of_vehicles_assigned = self.resources_used["number_of_vehicles_assigned"]

    def _calculate_solution_resources(self, solution: Solution) -> Dict[str, float]:
        total_resources = {}
        for vehicle_idx, route in solution.items():
            resources = self.resource_calc.calculate_route_resources(
                vehicle_idx, route)
            if resources is None:
                continue
            self.each_route_resource.append(resources)

            for resource, amount in resources.items():
                if resource not in total_resources:
                    total_resources[resource] = 0
                total_resources[resource] += amount

        total_resources["number_of_vehicles_assigned"] = len(
            self.each_route_resource)

        return total_resources

    def mutate(self, mutation_rate) -> SolutionChromosome:
        random_value = random()
        if random_value < mutation_rate:
            return self

        strategy_func = MutationStrategy.choose_mutation_strategy()
        return self

    def crossover(self, _other_solution_chromosome: SolutionChromosome) -> List[SolutionChromosome]:
        pass

    def __repr__(self) -> str:
        chromosome = f"Chromosome: {self.chromosome}"
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
            sep
        ]

        return "\n\t".join(_repr)

    def __eq__(self, _other_solution_chromosome: SolutionChromosome) -> bool:
        return self.solution == _other_solution_chromosome.solution

    def __gt__(self, _other_solution_chromosome: SolutionChromosome) -> bool:
        # 總配送車數最小化為主要目標，
        # 降低總配送距離與減少每趟次的花費時間為次要目標，
        # 以求取最佳的配送路線。所以目標函數(1)為最小化車輛的固定成本、
        # 車輛行駛的距離成本、每趟次花費的司機員薪資成本。
        self_resources = self.resources_used
        other_resources = _other_solution_chromosome.resources_used

        self_fuel_fee = self_resources['fuel_fee']
        self_driver_cost = self_resources['driver_cost']
        self_vehicle_fixed_cost = self_resources['vehicle_fixed_cost']
        self_total_cost = self_fuel_fee + self_driver_cost + self_vehicle_fixed_cost

        other_fuel_fee = other_resources['fuel_fee']
        other_driver_cost = other_resources['driver_cost']
        other_vehicle_fixed_cost = other_resources['vehicle_fixed_cost']
        other_total_cost = other_fuel_fee + other_driver_cost + other_vehicle_fixed_cost

        return self_total_cost < other_total_cost

    @ property
    def fitness(self):
        pass
