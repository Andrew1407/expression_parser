from types import NoneType
from expression_parser.parser.tokens import Operator
from expression_parser.analyzer.tree_nodes import Node, BinaryOperatorNode, FunctionNode


def flat_operations(node: Node, container: list[Node]):
  match node:
    case BinaryOperatorNode():
      flat_operations(node.left, container)
      flat_operations(node.right, container)
      container.append(node)
    case FunctionNode():
      for arg in node.args: flat_operations(arg, container)
      container.append(node)


def is_nested(node: Node) -> bool:
  match node:
    case BinaryOperatorNode():
      return any(isinstance(n, BinaryOperatorNode) or (isinstance(n, FunctionNode) and n.args > 0) for n in (node.left, node.right))
    case FunctionNode():
      return node.args > 0
    case _:
      return False


def take_flat(container: list[Node]) -> (Node | NoneType):
  flat = tuple((i, n) for i, n in enumerate(container) if not is_nested(n))
  if not flat: return None
  position, found = flat[0]
  container.pop(position)
  return found


def take_ready(left: list[Node], fulfilled: list[Node]) -> (Node | NoneType):
  is_fulfilled = lambda n: any(n is f for f in fulfilled)
  # print(f'{left=}')
  for i, n in enumerate(left):
    children = None
    match n:
      case BinaryOperatorNode():
        children = n.left, n.right
      case FunctionNode():
        children = n.args
    if not children: continue
    ready = all(is_fulfilled(c) for c in children if isinstance(c, (BinaryOperatorNode, FunctionNode)))
    if ready:
      left.pop(i)
      return n
  return None


def take_congenerical(left: list[Node], previous_layers: list[Node | NoneType]) -> (Node | NoneType):
  for i, n in enumerate(left):
    if n.value.value not in (Operator.PLUS.value, Operator.MULTIPLY.value):
      return None
    children = tuple(p for p in previous_layers if n.left is p or n.right is p)
    fit = children and all(c.value.value == n.value.value for c in children)
    if not fit: continue
    print(f'{fit} {previous_layers=}')
    left.pop(i)
    return n
  return None
