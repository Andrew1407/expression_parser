from copy import deepcopy
from expression_parser.parser.tokens import Operator
from expression_parser.analyzer.tree_nodes import Node, BinaryOperatorNode, UnaryOperatorNode, FunctionNode, NodesTuple
from .utils import get_binary_forms_collection, get_function_forms_collection, get_unary_forms_collection


def generate_commutativity_forms(node: Node) -> NodesTuple:
  match node:
    case BinaryOperatorNode():
      swap_included = node.value.value in (Operator.PLUS.value, Operator.MULTIPLY.value)
      return get_binary_forms_collection(node, generate_commutativity_forms, swap_included)
    case UnaryOperatorNode():
      return get_unary_forms_collection(node, generate_commutativity_forms)
    case FunctionNode():
      return get_function_forms_collection(node, generate_commutativity_forms)
    case _:
      return (node,)
