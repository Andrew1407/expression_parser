from copy import deepcopy
from expression_parser.parser.tokens import Token, Operator, TokenType
from expression_parser.analyzer.tree_nodes import Node, BinaryOperatorNode, UnaryOperatorNode, FunctionNode, NodesTuple
from .utils import get_binary_forms_collection
from .utils import get_binary_forms_collection, get_function_forms_collection, get_unary_forms_collection


def generate_distributivity_forms(node: Node) -> NodesTuple:
  match node:
    case BinaryOperatorNode(value=Token(value=Operator.MULTIPLY.value)):
      return (deepcopy(node), *get_multiplications(node))
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
  forms: list[Node] = list()
  left_forms = generate_distributivity_forms(node.left)
  right_forms = generate_distributivity_forms(node.right)
  for left_form in left_forms:
    for right_form in right_forms:
      nodes_left: list[Node] = list()
      nodes_right: list[Node] = list()
      search_plus_nodes(left_form, nodes_left)
      search_plus_nodes(right_form, nodes_right)
      if len(nodes_left) == 1 and len(nodes_right) == 1:
        continue
      joined: list[Node] = list()
      for nl in nodes_left:
        for nr in nodes_right:
          node = BinaryOperatorNode(
            value=Token.of(Operator.MULTIPLY.value, TokenType.OPERATOR, nl.value.start),
            left=nl,
            right=nr,
          )
          joined.append(node)
      joined = join_nodes_with_operator(joined, Operator.PLUS.value)
      forms.append(joined)
  return tuple(forms)


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
