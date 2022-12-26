from types import NoneType
from expression_parser.parser.tokens import Token, Operator
from expression_parser.analyzer.tree_nodes import Node, BinaryOperatorNode, FunctionNode
from .utils import flat_operations, take_flat, take_ready, take_congenerical
from .containers import ConveyorStep, OperationDuration, SimulationData

from expression_parser.tree_output.str_converter import stringify_tree


class DynamicConveyor:
  def __init__(self, expression: Node, layers: int = 1):
    self.__steps: list[ConveyorStep] = list()
    self.__layers: int = layers
    self.__operations_fulfileld: list[Node] = list()
    self.__operations_left: list[Node] = list()
    flat_operations(expression, self.__operations_left)
    self.__operations_count: int = len(self.__operations_left)

  
  def simulate(self) -> SimulationData:
    while len(self.__operations_fulfileld) < self.__operations_count:
      if not self.__steps:
        node = self.__take()
        layers = [None] * self.__layers
        layers[0] = node
        layers = tuple(layers)
        step = ConveyorStep(layers=layers, tacts=self.__calc_step_tacts(layers))
        self.__steps.append(step)
        if self.__layers == 1:
          if node:
            self.__operations_fulfileld.append(node)
        continue
      previous_layers = self.__steps[-1].layers
      fulfilled = previous_layers[-1]
      # print(f'{previous_layers=}')
      if fulfilled:
        self.__operations_fulfileld.append(fulfilled)
      node = self.__take()
      layers = tuple([node, *previous_layers[:-1]])
      step = ConveyorStep(layers=layers, tacts=self.__calc_step_tacts(layers))
      if step.tacts > 0:
        self.__steps.append(step)
    return self.__generate_results()


  def __generate_results(self) -> SimulationData:
    result = SimulationData(steps=tuple(self.__steps))
    result.sequential = self.__layers * sum(self.__get_tacts(n) for n in self.__operations_fulfileld)
    result.dynamic = sum(s.tacts for s in self.__steps)
    return result


  def __take(self) -> (Node | NoneType):
    found = take_flat(self.__operations_left)
    if found: return found
    found = take_ready(self.__operations_left, self.__operations_fulfileld)
    if found: return found
    found = take_congenerical(self.__operations_left, self.__steps[-1].layers)
    if found: print(len(self.__steps) + 1, stringify_tree(found))
    return found
    

  def __calc_step_tacts(self, layers: list[Node | NoneType]) -> float:
    return max(self.__get_tacts(n) for n in layers)


  def __get_tacts(self, node: Token) -> float:
    match node:
      case FunctionNode():
        return OperationDuration.FUNCTION
      case BinaryOperatorNode(value=Token(value=Operator.PLUS.value)):
        return OperationDuration.PLUS
      case BinaryOperatorNode(value=Token(value=Operator.MINUS.value)):
        return OperationDuration.MIN
      case BinaryOperatorNode(value=Token(value=Operator.MULTIPLY.value)):
        return OperationDuration.MUL
      case BinaryOperatorNode(value=Token(value=Operator.DIVIDE.value)):
        return OperationDuration.DIV
      case BinaryOperatorNode(value=Token(value=Operator.POWER.value)):
        return OperationDuration.POW
      case None:
        return 0
