from copy import deepcopy
from expression_parser.parser.tokens import Token, Operator, TokenType
from expression_parser.analyzer.tree_nodes import Node, BinaryOperatorNode, UnaryOperatorNode, FunctionNode, NodesTuple
from .utils import get_binary_forms_collection, get_function_forms_collection, get_unary_forms_collection


def generate_distributivity_forms(node: Node) -> NodesTuple:
  match node:
    case BinaryOperatorNode(value=Token(value=Operator.MULTIPLY.value)):
      return get_multiplications(node)
    case BinaryOperatorNode(value=Token(value=Operator.DIVIDE.value)):
      return (deepcopy(node), *get_divisions(node))
    case BinaryOperatorNode():
      variants = get_binary_forms_collection(node, generate_distributivity_forms)
      return variants
    case FunctionNode():
      return get_function_forms_collection(node, generate_distributivity_forms)
    case UnaryOperatorNode():
      return get_unary_forms_collection(node, generate_distributivity_forms)
    case _:
      return (node,)


def get_multiplications(node: BinaryOperatorNode) -> NodesTuple:
  left_forms = get_plus_nodes_combinations(node.left)
  right_forms = get_plus_nodes_combinations(node.right)
  left_combinations = make_multiplication_combinations(left_forms, right_forms)
  right_combinations = make_multiplication_combinations(right_forms, left_forms, swapped=True)
  forms = join_combinations(left_combinations + right_combinations)
  return tuple(forms)


def get_plus_nodes_combinations(node: Node) -> list[list[Node]]:
  combinations: list[list[Node]] = list()
  match node:
    case BinaryOperatorNode(value=Token(value=Operator.PLUS.value)):
      combinations.append([deepcopy(node)])
      left_forms = generate_distributivity_forms(node.left)
      right_forms = generate_distributivity_forms(node.right)
      for left_form in left_forms:
        for right_form in right_forms:
          left_nodes = get_plus_nodes_combinations(left_form)
          right_nodes = get_plus_nodes_combinations(right_form)
          for left in left_nodes:
            for right in right_nodes:
              combinations.append([deepcopy(n) for n in left + right])
    case _:
      combinations.extend([[deepcopy(n)] for n in generate_distributivity_forms(node)])
  return combinations
      

def get_divisions(node: BinaryOperatorNode) -> Node:
  forms: list[Node] = list()
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
  uppers = generate_distributivity_forms(join_nodes_with_operator(upper_nodes, Operator.MULTIPLY.value))
  lowers = generate_distributivity_forms(join_nodes_with_operator(lower_nodes, Operator.MULTIPLY.value))
  for upper in uppers:
    for lower in lowers:
      forms.append(set_division_node(upper, lower))
  return tuple(forms)


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


def make_multiplication_combinations(node_groups: list[list[Node]], target_groups: list[list[Node]], swapped: bool = False) -> list[list[list[list[Node]]]]:
  combinations: list[list[list[list[Node]]]] = list()
  for nodes in node_groups:
    group: list[list[list[Node]]] = list()
    for node in nodes:
      combined: list[list[Node]] = list()
      for targets in target_groups:
        multiplied: list[node] = list()
        for target in targets:
          bound = BinaryOperatorNode(
            value=Token.of(Operator.MULTIPLY.value, TokenType.OPERATOR),
            left=deepcopy(target if swapped else node),
            right=deepcopy(node if swapped else target),
          )
          bound.value.start = bound.left.value.start
          multiplied.append(bound)
        combined.append(multiplied)
      group.append(combined)
    combinations.append(group)
  return combinations


def join_combinations(combinations: list[list[list[list[Node]]]]) -> list[Node]:
  joined_nodes: list[Node] = list()
  for group in combinations:
    variants: list[list[Node]] = list()
    for forms in group:
      if not variants:
        variants.extend(deepcopy(f) for f in forms)
        continue
      combinations_extended = list()
      for form in forms:
        for combination in deepcopy(variants):
          combination.extend(deepcopy(f) for f in form)
          combinations_extended.append(combination)
      variants = combinations_extended
    joined_nodes.extend(join_nodes_with_operator(v, Operator.PLUS.value) for v in variants)
  return joined_nodes
