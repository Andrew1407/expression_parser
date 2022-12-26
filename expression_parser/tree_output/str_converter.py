from typing import Callable
from expression_parser.parser.tokens import Token, Operator
from expression_parser.analyzer.tree_nodes import Node, UnaryOperatorNode, FunctionNode, BinaryOperatorNode


def stringify_tree(node: Node) -> str:
  if not node.value: return str()
  str_value = node.value.value
  match node:
    case BinaryOperatorNode(value=Token(value=Operator.PLUS.value)):
      return ' '.join((stringify_tree(node.left), str_value,stringify_tree(node.right)))
    case BinaryOperatorNode(value=Token(value=Operator.MINUS.value)):
      plus_check = __operator_check(Operator.isunary)
      return wrap_in_brackets(operator=node, rules=(None, plus_check))
    case BinaryOperatorNode(value=Token(value=Operator.MULTIPLY.value)):
      plus_check = __operator_check(Operator.isunary)
      return wrap_in_brackets(operator=node, rules=(plus_check, plus_check))
    case BinaryOperatorNode(value=Token(value=Operator.DIVIDE.value)):
      return wrap_in_brackets(operator=node, rules=(
        __operator_check(Operator.isunary),
        __operator_check(lambda n: Operator.isop(n) and n != Operator.POWER.value),
      ))
    case BinaryOperatorNode(value=Token(value=Operator.POWER.value)):
      isop = lambda n: isinstance(n, BinaryOperatorNode)
      return wrap_in_brackets(operator=node, rules=(isop, isop))
    case FunctionNode():
      args = ', '.join(stringify_tree(arg) for arg in node.args)
      return f'{str_value}({args})'
    case UnaryOperatorNode():
      expression = stringify_tree(node.expression)
      if Operator.isop(node.expression.value.value):
        expression = f'({expression})'
      return str_value + expression
    case Node():
      return str_value


def wrap_in_brackets(operator: BinaryOperatorNode, rules: tuple[Callable[[Node], bool], Callable[[Node], bool]]) -> str:
  nodes = (operator.left, operator.right)
  stringified = tuple(stringify_tree(n) for n in nodes)
  wrappable = tuple(callable(rule) and rule(n) for n, rule in zip(nodes, rules))
  left, right = tuple(f'({s})' if r else s for s, r in zip(stringified, wrappable))
  return ' '.join((left, operator.value.value,right))


def __operator_check(check: Callable[[str], bool]) -> Callable[[Node], bool]:
  return lambda n: isinstance(n, BinaryOperatorNode) and check(n.value.value)
