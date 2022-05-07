from typing import Callable, List
from random import choice, random
import math


class MutationStrategy:
    def __init__(self, immutable_depot_names:List[int]) -> None:
        self.immutable_depot_names = immutable_depot_names

    def reverse_mutate(self, route: List[int]) -> List[int]:
        copy_route = route.copy()
        while True:
            left_ptr, right_ptr = self._randomly_choose_two_different_index_positions(route) # returning list of 'index'
            if not self._is_reverse_mutation_affecting_immutable_depots(route, [left_ptr, right_ptr]):
                break
        
        while (left_ptr < right_ptr):
            self._swap_depots(copy_route, left_ptr, right_ptr)

            left_ptr += 1
            right_ptr -= 1
        return copy_route

    def _is_reverse_mutation_affecting_immutable_depots(self,route:List[int],affecting_route_idx: List[int]) -> bool:

        start_idx, end_idx = affecting_route_idx  # e.g., 2, 4
        affecting_route = route[start_idx: end_idx+1 ] #route: [0, 1,2,3,4,5,6,0] -> [2,3,4]
        for depot in affecting_route:
            if depot in self.immutable_depot_names:
                return True

        return False
        

    def two_points_mutate(self, route: List[int]) -> List[int]:
        copy_route = route.copy()
        
        while True:
            left_ptr, right_ptr = self._randomly_choose_two_different_index_positions(route)
            if not self._is_two_points_mutation_affecting_immutable_depots(route, [left_ptr, right_ptr]):
                break

        self._swap_depots(copy_route, left_ptr, right_ptr)

        return copy_route

    def _is_two_points_mutation_affecting_immutable_depots(self, route: List[int], affecting_route_idx: List[int]) -> bool:
        
        for route_idx in affecting_route_idx:
            depot = route[route_idx]
            if depot in self.immutable_depot_names:
                return True
        return False
        

    def _randomly_choose_index_position(self, route:List[int]) -> int:

        while True:
            random_idx = math.floor((random() * len(route)))
            if (route[random_idx] != 0):
                break
        return random_idx

    def _randomly_choose_two_different_index_positions(self, route:List[int]) -> List[int]:
        
        while True:
            first_point = self._randomly_choose_index_position(route)
            second_point = self._randomly_choose_index_position(route)
            if (second_point != first_point):
                break
        left_ptr = min(first_point, second_point)
        right_ptr = max(first_point, second_point)
        
        return [left_ptr, right_ptr]

    def _swap_depots(self, route: List[int], x_idx:int, y_idx:int) -> None:
        route[x_idx], route[y_idx] = route[y_idx], route[x_idx]

    def randomly_choose_mutation_strategy(self) -> Callable:
        all_strategies = [self.reverse_mutate, self.two_points_mutate]
        return choice(all_strategies)


        