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


def generate_commutativity_forms(node: Node) -> tuple[Node]:
  forms: list[Node] = list()
  match node:
    case BinaryOperatorNode():
      left_forms = generate_commutativity_forms(node.left)
      right_forms = generate_commutativity_forms(node.right)
      for left in left_forms:
        for right in right_forms:
          clone = deepcopy(node)
          clone.left = left
          clone.right = right
          forms.append(clone)
          if node.value.value in (Operator.PLUS.value, Operator.MULTIPLY.value):
            clone_inverted = deepcopy(node)
            clone_inverted.left = right
            clone_inverted.right = left
            forms.append(clone_inverted)
    case UnaryOperatorNode():
      expressions = generate_commutativity_forms(node.expression)
      for expression in expressions:
        clone = deepcopy(node)
        clone.expression = expression
        forms.append(clone)
    case _:
      forms.append(node)
  return tuple(forms)
