from typing import Callable
from types import NoneType
from copy import deepcopy
from parser.tokens import Token, TokenType, Operator
from analyzer.tree_nodes import Node, FunctionNode, UnaryOperatorNode, BinaryOperatorNode
from . import optimizer_tools


def build_parallel_tree(node: Node, convert_to_optimized: bool = True) -> Node:
  tree = deepcopy(node)
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
      balanse_operator(operator, binary, depth_builder)
    case BinaryOperatorNode(value=(Token(value=Operator.POWER.value))) as power:
      minimize_depth(power.left)
      minimize_depth(power.right)
    case FunctionNode() as function:
      for expression in function.args:
        minimize_depth(expression)


def balanse_operator(operator: str, node: BinaryOperatorNode, depth_builder: Callable[[Node, list[Node]], NoneType]):
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
  left_plus = binary.left.value.value == operator
  right_plus = binary.right.value.value == operator
  if left_plus and right_plus:
    depth_warapper = lambda node, depth: get_path_depth(node, depth, operator)
    max_path, _ = get_leaves_path(binary, depth_warapper)
    depth.extend(max_path)
    return
  depth.append(binary)
  if left_plus and not right_plus:
    get_path_depth(binary.right, depth, operator)
  if right_plus and not left_plus:
    get_path_depth(binary.left, depth, operator)


def get_leaves_path(node: BinaryOperatorNode, depth_builder: Callable[[Node, list[Node]], NoneType]) -> tuple[list[Node], list[Node]]:
  left_depth: list[Node] = [node]
  right_depth: list[Node] = [node]
  depth_builder(node.left, left_depth)
  depth_builder(node.right, right_depth)
  left_max = len(left_depth) > len(right_depth)
  return (left_depth, right_depth) if left_max else (right_depth, left_depth)
