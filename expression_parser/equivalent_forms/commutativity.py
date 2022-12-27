from copy import deepcopy
from expression_parser.parser.tokens import Operator
from expression_parser.analyzer.tree_nodes import Node, BinaryOperatorNode, UnaryOperatorNode


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
