from typing import Callable
from copy import deepcopy
from expression_parser.analyzer.tree_nodes import Node, BinaryOperatorNode, UnaryOperatorNode, FunctionNode,  NodesTuple


def get_binary_forms_collection(node: BinaryOperatorNode, factory: Callable[[Node], NodesTuple], swap_included: bool = False) -> NodesTuple:
  forms: list[Node] = list()
  left_forms = factory(node.left)
  right_forms = factory(node.right)
  for left in left_forms:
    for right in right_forms:
      clone = deepcopy(node)
      clone.left = deepcopy(left)
      clone.right = deepcopy(right)
      forms.append(clone)
      if swap_included:
        clone_inverted = deepcopy(node)
        clone_inverted.left = deepcopy(right)
        clone_inverted.right = deepcopy(left)
        forms.append(clone_inverted)
  return tuple(forms)


def get_function_forms_collection(node: FunctionNode, factory: Callable[[Node], NodesTuple]) -> NodesTuple:
  if not node.args: return (node,)
  forms: list[Node] = list()
  arg_forms = tuple(factory(arg) for arg in node.args)
  combinations: list[list[Node]] = list()
  for form in arg_forms:
    if not combinations:
      combinations.extend([arg] for arg in form)
      continue
    combinations_extended = list()
    for arg in form:
      for combination in deepcopy(combinations):
        combination.append(arg)
        combinations_extended.append(combination)
    combinations = combinations_extended
  for combination in combinations:
    fn = deepcopy(node)
    fn.args = tuple(combination)
    forms.append(fn)
  return tuple(forms)


def get_unary_forms_collection(node: UnaryOperatorNode, factory: Callable[[Node], NodesTuple]) -> NodesTuple:
  forms: list[Node] = list()
  expressions = factory(node.expression)
  for expression in expressions:
    clone = deepcopy(node)
    clone.expression = expression
    forms.append(clone)
  return tuple(forms)
