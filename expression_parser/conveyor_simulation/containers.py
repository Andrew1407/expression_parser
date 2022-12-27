from types import NoneType
from dataclasses import dataclass
from expression_parser.analyzer.tree_nodes import Node


LAYERS_COUNT = 4


class OperationDuration:
  PLUS: float = 1
  MIN: float = 1
  MUL: float = 2
  DIV: float = 5
  POW: float = 7
  FUNCTION: float = 10


@dataclass
class ConveyorStep:
  tacts: float
  layers: tuple[Node | NoneType]


@dataclass
class SimulationData:
  steps: tuple[ConveyorStep]
  layers: int = 1
  sequential: float = 0
  dynamic: float = 0
  acceleration: float = 0
  efficiency: float = 0

  def format_params(self, round_digits: int = 7) -> str:
    params = 'sequential', 'dynamic', 'acceleration', 'efficiency'
    sequence = tuple(f'{p} = {round(getattr(self, p), round_digits)}' for p in params)
    return '; '.join(sequence) + ';'
