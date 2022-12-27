from typing import Callable
from types import NoneType
from copy import deepcopy
from expression_parser.parser.tokens import Token, TokenType, Operator
from expression_parser.analyzer.tree_nodes import Node, FunctionNode, UnaryOperatorNode, BinaryOperatorNode
from . import optimizer_tools


def build_parallel_tree(node: Node, convert_to_optimized: bool = True) -> Node:
  tree = deepcopy(node)
  if not tree.value: return tree
  tree = optimizer_tools.minimize_redundant_nodes(tree)
  optimizer_tools.convert_to_primitive(tree)
  tree, unary = optimizer_tools.get_unary_min_depth(tree)
  if unary:
    unary.expression = tree
    tree = unary
  optimizer_tools.reduce_unaries(tree)
  tree = optimizer_tools.open_brackets(tree)
  minimize_depth(tree)
  if convert_to_optimized:
    tree = optimizer_tools.convert_to_optimized(tree)
  return tree


def minimize_depth(node: Node):
  match node:
    case UnaryOperatorNode() as unary:
      minimize_depth(unary.expression)
    case BinaryOperatorNode() as binary if binary.value.value in (Operator.PLUS.value, Operator.MULTIPLY.value):
      operator = binary.value.value
      depth_builder = lambda node, depth: get_path_depth(node, depth, operator)
      balance_operator(operator, binary, depth_builder)
    case BinaryOperatorNode(value=(Token(value=Operator.POWER.value))) as power:
      minimize_depth(power.left)
      minimize_depth(power.right)
    case FunctionNode() as function:
      for expression in function.args:
        minimize_depth(expression)


def balance_operator(operator: str, node: BinaryOperatorNode, depth_builder: Callable[[Node, list[Node]], NoneType]):
  max_path, min_path = get_leaves_path(node, depth_builder)
  max_len = len(max_path)
  min_len = len(min_path)
  if max_len != min_len and max_len > 2:
    joinable, prev, replaceable = tuple(max_path[-3:])
    leaf_left = 'left' if prev.right is replaceable else 'right'
    leaf_to_place = 'left' if joinable.left is prev  else 'right'
    setattr(joinable, leaf_to_place, getattr(prev, leaf_left))

    prev, groupable = tuple(min_path[-2:])
    leaf_to_add = 'left' if prev.left is groupable else 'right'
    grouped = BinaryOperatorNode(
      value=Token.of(operator, TokenType.OPERATOR, groupable.value.start),
      left=replaceable,
      right=groupable,
    )
    setattr(prev, leaf_to_add, grouped)

  minimize_depth(node.left)
  minimize_depth(node.right)


def get_path_depth(node: Node, depth: list[Node], operator: str):
  is_binary = isinstance(node, BinaryOperatorNode)
  if not is_binary or is_binary and node.value.value != operator:
    depth.append(node)
    return
  binary: BinaryOperatorNode = node
  left_operator = binary.left.value.value == operator
  right_operator = binary.right.value.value == operator
  if left_operator and right_operator:
    depth_warapper = lambda node, depth: get_path_depth(node, depth, operator)
    max_path, _ = get_leaves_path(binary, depth_warapper)
    depth.extend(max_path)
    return
  depth.append(binary)
  if left_operator and not right_operator:
    get_path_depth(binary.right, depth, operator)
  elif right_operator and not left_operator:
    get_path_depth(binary.left, depth, operator)
  elif not (left_operator or right_operator):
    binary_left = isinstance(binary.left, BinaryOperatorNode)
    binary_right = isinstance(binary.right, BinaryOperatorNode)
    if binary_left and not binary_right:
      depth.append(binary.right)
    elif binary_right and not binary_left:
      depth.append(binary.left)
    elif binary_left and binary_right:
      left_warapper = lambda node, depth: get_path_depth(node, depth, binary.left.value.value)
      max_left, _ = get_leaves_path(binary.left, left_warapper)
      right_warapper = lambda node, depth: get_path_depth(node, depth, binary.right.value.value)
      max_right, _ = get_leaves_path(binary.right, right_warapper)
      shortest = max_left[0] if len(max_left) > len(max_right) else max_right[0]
      depth.append(shortest)


def get_leaves_path(node: BinaryOperatorNode, depth_builder: Callable[[Node, list[Node]], NoneType]) -> tuple[list[Node], list[Node]]:
  left_depth: list[Node] = [node]
  right_depth: list[Node] = [node]
  depth_builder(node.left, left_depth)
  depth_builder(node.right, right_depth)
  left_max = len(left_depth) > len(right_depth)
  return (left_depth, right_depth) if left_max else (right_depth, left_depth)
