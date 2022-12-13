from expression_parser.parser.tokens import Operator
from expression_parser.analyzer.tree_nodes import Node, BinaryOperatorNode, UnaryOperatorNode, FunctionNode
from expression_parser.parallel_tree.optimizer_tools import open_brackets
from .utils import apply_minus_copy_wrapper


@apply_minus_copy_wrapper
def apply_commutation(node: Node) -> Node:
  swap_nodes(node)
  return node


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
      node.args = tuple(swap_nodes(arg) for arg in node.args)
    case UnaryOperatorNode():
      swap_nodes(node.expression)
