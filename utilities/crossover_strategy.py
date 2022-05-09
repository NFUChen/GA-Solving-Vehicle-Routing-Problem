from typing import Callable, List
from random import choice

class CrossoverStrategy:
  def __init__(self, immutable_depot_names:List[int]) -> None:
        self.immutable_depot_names = immutable_depot_names
        self.MAXIMUM_ATTEMPT = 10

    
  
