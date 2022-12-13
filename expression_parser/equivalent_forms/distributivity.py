from expression_parser.parser.tokens import Token, Operator, TokenType
from expression_parser.analyzer.tree_nodes import Node, BinaryOperatorNode, UnaryOperatorNode, FunctionNode
from expression_parser.parallel_tree.optimizer_tools import open_brackets
from .utils import apply_minus_copy_wrapper


@apply_minus_copy_wrapper
def apply_distribution(node: Node) -> Node:
  return apply_operator(node)


def apply_operator(node: Node) -> Node:
  match node:
    case BinaryOperatorNode(value=Token(value=Operator.MULTIPLY.value)):
      return multiply_nodes(node)
    case BinaryOperatorNode(value=Token(value=Operator.DIVIDE.value)):
      return divide_nodes(node)
    case BinaryOperatorNode():
      node.left = apply_operator(node.left)
      node.right = apply_operator(node.right)
      return node
    case FunctionNode():
      node.args = tuple(apply_operator(arg) for arg in node.args)
      return node
    case Node():
      return node 
          

def multiply_nodes(node: BinaryOperatorNode) -> Node:
  node.left = apply_operator(node.left)
  node.right = apply_operator(node.right)
  nodes_left: list[Node] = list()
  nodes_right: list[Node] = list()
  search_plus_nodes(node.left, nodes_left)
  search_plus_nodes(node.right, nodes_right)
  if len(nodes_left) == 1 and len(nodes_right) == 1:
    return node
  joined: list[Node] = list()
  for nl in nodes_left:
    for nr in nodes_right:
      node = BinaryOperatorNode(
        value=Token.of(Operator.MULTIPLY.value, TokenType.OPERATOR, nl.value.start),
        left=nl,
        right=nr,
      )
      joined.append(node)
  return join_nodes_with_operator(joined, Operator.PLUS.value)


def divide_nodes(node: BinaryOperatorNode) -> Node:
  upper_nodes: list[Node] = list()
  lower_nodes: list[Node] = list()
  current_node = node
  to_upper = True
  while True:
    nodes = upper_nodes if to_upper else lower_nodes
    if current_node.value.value != Operator.DIVIDE.value:
      nodes.append(current_node)
      break
    nodes.append(current_node.left)
    current_node = current_node.right
    to_upper = not to_upper
  upper = apply_operator(join_nodes_with_operator(upper_nodes, Operator.MULTIPLY.value))
  lower = apply_operator(join_nodes_with_operator(lower_nodes, Operator.MULTIPLY.value))
  divided = set_division_node(upper, lower)
  return divided


def join_nodes_with_operator(nodes: list[Node], operator: str) -> Node:
  last_node = nodes[-1]
  if len(nodes) == 1:
    return last_node
  main_node: Node = None
  current_node: Node = None
  for node in nodes[:-1]:
    created = BinaryOperatorNode(
      value=Token.of(operator, TokenType.OPERATOR, node.value.end),
      left=node,
      right=None,
    )
    if main_node is None:
      main_node = created
    else:
      current_node.right = created
    current_node = created
  current_node.right = last_node
  return main_node


def search_plus_nodes(node: Node, nodes: list[Node]):
  match node:
    case BinaryOperatorNode(value=Token(value=Operator.PLUS.value)):
      search_plus_nodes(node.left, nodes)
      search_plus_nodes(node.right, nodes)
    case _:
      nodes.append(node)


def set_division_node(node: Node, division: Node) -> Node:
  match node:
    case BinaryOperatorNode(value=Token(value=Operator.PLUS.value)):
      node.left = set_division_node(node.left, division)
      node.right = set_division_node(node.right, division)
      return node
    case _:
      return BinaryOperatorNode(
        value=Token.of(Operator.DIVIDE.value, TokenType.OPERATOR, node.value.start),
        left=node,
        right=division,
      )
