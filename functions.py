from dataclasses import dataclass
from typing import Callable
import math as mt

@dataclass
class FunctionDescriptor:
  function: Callable
  args: int


functions: dict[str, FunctionDescriptor] = dict(
  sin=FunctionDescriptor(function=mt.sin, args=1),
)
