from types import NoneType
from dataclasses import dataclass
from expression_parser.analyzer.tree_nodes import Node


class OperationDuration:
  PLUS: float = 1
  MIN: float = 1
  MUL: float = 2
  DIV: float = 5
  POW: float = 4
  FUNCTION: float = 5


@dataclass
class ConveyorStep:
  tacts: float
  layers: tuple[Node | NoneType]


@dataclass
class SimulationData:
  steps: tuple[ConveyorStep]
  sequential: float = 0
  dynamic: float = 0
  acceleration: float = 0
  efficiency: float = 0
