from typing import Callable, List
from random import choice, random
import math


class MutationStrategy:
    @staticmethod
    def reverse_mutate(cls, route: List[int]) -> None:
        pass

    @staticmethod
    def two_points_mutate(route: List[int]) -> None:
        pass

    @classmethod
    def choose_mutation_strategy(cls) -> Callable:
        all_strategy = [cls.reverse_mutate, cls.two_points_mutate]
        return choice(all_strategy)


# def randomly_choose_index_position(route:List[int]) -> int:
#     is_choosing_warehose_depot = True
#     while (is_choosing_warehose_depot):
#         random_idx = math.floor((random() * len(route)))
#         if (route[random_idx] != 0):
#             is_choosing_warehose_depot = False
#     return random_idx

# def randomly_choose_two_different_index_positions(route:List[int]) -> List[int]:
#     first_point = randomly_choose_index_position(route)
#     second_point = randomly_choose_index_position(route)
#     while second_point == first_point:
#         second_point = randomly_choose_index_position(route)
#     left_ptr = min(first_point, second_point)
#     right_ptr = max(first_point, second_point)
    
#     return [left_ptr, right_ptr]


# def swap_depots(route:List[int], x, y) -> None:
#     route[x], route[y] = route[y], route[x]

# def reverse_mutate(route:List[int]) -> None:
#     left_ptr, right_ptr = randomly_choose_two_different_index_positions()
    
#     print(left_ptr, right_ptr)
#     while (left_ptr < right_ptr):
#         swap_depots(route, left_ptr, right_ptr)
        
#         left_ptr += 1
#         right_ptr -= 1

# def two_points_mutate(route:List[int]) -> None:
#     left_ptr, right_ptr = randomly_choose_two_different_index_positions()
#     swap_depots(route, left_ptr, right_ptr)
        