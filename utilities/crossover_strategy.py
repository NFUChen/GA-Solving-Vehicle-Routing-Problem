from typing import List, Dict
from copy import deepcopy
from random import choice
Solution = Dict[int, List[int]]


class CrossoverStrategy:
    def __init__(self, solution: Solution, immutable_depot_names: List[int], vehicles_can_be_chosen_for_crossover: List[int]) -> None:
        self.solution = deepcopy(solution)
        self.immutable_depot_names = immutable_depot_names
        self.vehicles_can_be_chosen_for_crossover = vehicles_can_be_chosen_for_crossover
        self.MAXIMUM_ATTEMPT = 3

    def single_point_crossover(self, _other_solution: Solution, other_solution_chromosome_vehicles_can_be_chosen_for_crossover: List[int]) -> List[Solution]:
        if (len(other_solution_chromosome_vehicles_can_be_chosen_for_crossover) == 0 or len(self.vehicles_can_be_chosen_for_crossover) == 0):
            return [self.solution, _other_solution]

        _other_solution = deepcopy(_other_solution)
        self_vehicle_idx = self._randomly_choose_a_vehicle()
        other_vehicle_idx = self._randomly_choose_a_vehicle_for_other_solution(
            other_solution_chromosome_vehicles_can_be_chosen_for_crossover)

        number_of_attempts_to_find_index = 0
        while number_of_attempts_to_find_index < self.MAXIMUM_ATTEMPT:
            self_depot = self._randomly_choose_a_depot_in_a_route(
                self.solution[self_vehicle_idx])
            other_depot = self._randomly_choose_a_depot_in_a_route(
                _other_solution[other_vehicle_idx])
            number_of_attempts_to_find_index += 1
            if self_depot != other_depot:
                break
            
        self_depot_idx = self.solution[self_vehicle_idx].index(self_depot)
        other_depot_idx = _other_solution[other_vehicle_idx].index(other_depot)

        self.solution[self_vehicle_idx].remove(self_depot)
        self.solution[self_vehicle_idx].insert(self_depot_idx, other_depot)

        _other_solution[other_vehicle_idx].remove(other_depot)
        _other_solution[other_vehicle_idx].insert(other_depot_idx, self_depot_idx)

        return [self.solution, _other_solution]  # as child_x and child_y

    def _randomly_choose_a_vehicle(self) -> int:
        return choice(self.vehicles_can_be_chosen_for_crossover)

    def _randomly_choose_a_vehicle_for_other_solution(self, other_solution_chromosome_vehicles_can_be_chosen_for_crossover: List[int]) -> int:
        return choice(other_solution_chromosome_vehicles_can_be_chosen_for_crossover)

    def _randomly_choose_a_depot_in_a_route(self, route: List[int]) -> int:
        route_without_time_window_constraints = [depot_idx 
                                        for depot_idx in route 
                                        if not depot_idx in self.immutable_depot_names]

        return choice(route_without_time_window_constraints)
