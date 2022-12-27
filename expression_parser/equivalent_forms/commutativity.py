from copy import deepcopy
from expression_parser.parser.tokens import Operator
from expression_parser.analyzer.tree_nodes import Node, BinaryOperatorNode, UnaryOperatorNode, FunctionNode


def apply_commutation(node: Node) -> Node:
  tree = deepcopy(node)
  swap_nodes(tree)
  return tree


def swap_nodes(node: Node):
  match node:
    case BinaryOperatorNode():
      swap_nodes(node.left)
      swap_nodes(node.right)
      if node.value.value in (Operator.PLUS.value, Operator.MULTIPLY.value):
        left = node.left
        node.left = node.right
        node.right = left
    case FunctionNode():
      for arg in node.args: swap_nodes(arg)
    case UnaryOperatorNode():
      swap_nodes(node.expression)
