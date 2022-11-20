from typing import Literal, Callable
from types import NoneType
from copy import deepcopy
from parser.tokens import Token, TokenType, Operator, Signature
from analyzer.tree_nodes import Node, FunctionNode, UnaryOperatorNode, BinaryOperatorNode


class ParallelTreeBuilder:
  def __init__(self, tree: Node):
    self.__tree_raw: Node = tree
    self.__tree: Node = None

  
  def build(self) -> Node:
    self.__tree = deepcopy(self.__tree_raw)
    self.__convert_operations(self.__tree)
    self.__minimize_depth(self.__tree)
    return self.__tree

  
  def __convert_operations(self, node: Node):
    match node:
      case BinaryOperatorNode(value=(Token(value=Operator.MINUS.value))) as minus:
        self.__convert_operations(minus.left)
        self.__convert_operations(minus.right)
        right_wrapper = deepcopy(minus.value)
        right_wrapper.value = Operator.MINUS.value
        minus.value = Operator.PLUS.value
        minus.right = UnaryOperatorNode(value=right_wrapper, expression=minus.right)
      case BinaryOperatorNode(value=(Token(value=Operator.DIVIDE.value))) as division:
        self.__convert_operations(division.right)
        self.__convert_operations(division.left)
        one_constant = Token.of('1', TokenType.CONSTANT, division.value.start)
        division_by_one = deepcopy(division.value)
        division.value = Operator.MULTIPLY.value
        division.right = BinaryOperatorNode(value=division_by_one, left=one_constant, right=division.right)
      case UnaryOperatorNode() as unary:
        self.__convert_operations(unary.expression)
      case FunctionNode() as function:
        for expression in function.args:
          self.__convert_operations(expression)


  def __minimize_depth(self, node: Node):
    match node:
      case UnaryOperatorNode() as unary:
        self.__minimize_depth(unary.expression)
      case BinaryOperatorNode(value=(Token(value=Operator.PLUS.value))) as binary:
        self.__balanse_plus(binary)
      case BinaryOperatorNode(value=(Token(value=Operator.MULTIPLY.value))) as binary:
        self.__balanse_multiplication(binary)


  def __balanse_plus(self, node: BinaryOperatorNode):
    max_path, min_path = self.__get_path_leaves(node, self.__get_depth_path_plus)
    if len(max_path) != len(min_path):
      replaceable = max_path[-1]
      prev: BinaryOperatorNode = max_path[-2]
      i = -2
      while -1 <= i < -len(max_path) and isinstance(prev, UnaryOperatorNode):
        replaceable = max_path[-i]
        prev = max_path[-i - 1]
        i -= 1
      leaf: Literal['left', 'right'] = 'left' if prev.left is replaceable else 'right'
      leaf_left: Literal['left', 'right'] = 'left' if leaf == 'right' else 'right'
      while i <= -len(max_path):
        if isinstance(max_path[i], UnaryOperatorNode):
          i -= 1
        else:
          break
      leaf_to_place: Literal['left', 'right'] = 'left' if max_path[i - 1].left is max_path[i]  else 'right'
      setattr(max_path[i - 1], leaf_to_place, getattr(prev, leaf_left))

      groupable = min_path[-1]
      prev: BinaryOperatorNode = min_path[-2]
      i = -2
      while -1 <= i < -len(min_path) and isinstance(prev, UnaryOperatorNode):
        groupable = min_path[-i]
        prev = min_path[-i - 1]
        i -= 1
      leaf_to_add: Literal['left', 'right'] = 'left' if prev.left is groupable else 'right'
      grouped = BinaryOperatorNode(
        value=Token.of(Operator.PLUS.value, TokenType.OPERATOR, prev.value.start),
        left=replaceable,
        right=groupable,
      )
      setattr(prev, leaf_to_add, grouped)

    self.__minimize_depth(node.left)
    self.__minimize_depth(node.right)


  def __get_depth_path_plus(self, node: Node, depth: list[Node]):
    match node:
      case UnaryOperatorNode() as unary:
        depth.append(unary)
        self.__get_depth_path_plus(unary.expression, depth)
      case BinaryOperatorNode() as operator if operator.value.value != Operator.PLUS.value:
        depth.append(operator)
      case BinaryOperatorNode(value=(Token(value=Operator.PLUS.value))) as binary:
        left_plus = binary.left.value.value == Operator.PLUS.value
        right_plus = binary.right.value.value == Operator.PLUS.value
        if left_plus and right_plus:
          max_path, _ = self.__get_path_leaves(binary, self.__get_depth_path_plus)
          depth.extend(max_path)
          return
        depth.append(binary)
        if left_plus and not right_plus:
          self.__get_depth_path_plus(binary.right, depth)
        if right_plus and not left_plus:
          self.__get_depth_path_plus(binary.left, depth)
      case FunctionNode() as function:
        depth.append(function)
      case Node() as node:
        depth.append(node)

  
  def __balanse_multiplication(self, node: BinaryOperatorNode):
    max_path, min_path = self.__get_path_leaves(node, self.__get_depth_path_multiply)
    if len(max_path) != len(min_path):
      replaceable = max_path[-1]
      prev: BinaryOperatorNode = max_path[-2]
      i = -2
      while -1 <= i < -len(max_path) and isinstance(prev, UnaryOperatorNode):
        replaceable = max_path[-i]
        prev = max_path[-i - 1]
        i -= 1
      leaf: Literal['left', 'right'] = 'left' if prev.left is replaceable else 'right'
      leaf_left: Literal['left', 'right'] = 'left' if leaf == 'right' else 'right'
      while i <= -len(max_path):
        if isinstance(max_path[i], UnaryOperatorNode):
          i -= 1
        else:
          break
      leaf_to_place: Literal['left', 'right'] = 'left' if max_path[i - 1].left is max_path[i]  else 'right'
      setattr(max_path[i - 1], leaf_to_place, getattr(prev, leaf_left))

      groupable = min_path[-1]
      prev: BinaryOperatorNode = min_path[-2]
      i = -2
      while -1 <= i < -len(min_path) and isinstance(prev, UnaryOperatorNode):
        groupable = min_path[-i]
        prev = min_path[-i - 1]
        i -= 1
      leaf_to_add: Literal['left', 'right'] = 'left' if prev.left is groupable else 'right'
      grouped = BinaryOperatorNode(
        value=Token.of(Operator.MULTIPLY.value, TokenType.OPERATOR, prev.value.start),
        left=replaceable,
        right=groupable,
      )
      setattr(prev, leaf_to_add, grouped)

    self.__minimize_depth(node.left)
    self.__minimize_depth(node.right)


  def __get_depth_path_multiply(self, node: Node, depth: list[Node]):
    match node:
      case UnaryOperatorNode() as unary:
        depth.append(unary)
        self.__get_depth_path_multiply(unary.expression, depth)
      case BinaryOperatorNode() as operator if operator.value.value != Operator.MULTIPLY.value:
        depth.append(operator)
      case BinaryOperatorNode(value=(Token(value=Operator.MULTIPLY.value))) as binary:
        left_plus = binary.left.value.value == Operator.MULTIPLY.value
        right_plus = binary.right.value.value == Operator.MULTIPLY.value
        if left_plus and right_plus:
          max_path, _ = self.__get_path_leaves(binary, self.__get_depth_path_multiply)
          depth.extend(max_path)
          return
        depth.append(binary)
        if left_plus and not right_plus:
          self.__get_depth_path_multiply(binary.right, depth)
        if right_plus and not left_plus:
          self.__get_depth_path_multiply(binary.left, depth)
      case FunctionNode() as function:
        depth.append(function)
      case Node() as node:
        depth.append(node)


  def __get_path_leaves(self, node: BinaryOperatorNode, depth_builder: Callable[[Node, list[Node]], NoneType]) -> tuple[list[Node], list[Node]]:
    left_depth: list[Node] = [node]
    right_depth: list[Node] = [node]
    depth_builder(node.left, left_depth)
    depth_builder(node.right, right_depth)
    left_len = len(left_depth)
    right_len = len(right_depth)
    if self.__last_unary(left_depth): left_len -= 1
    if self.__last_unary(right_depth): right_len -= 1
    left_max = left_len > right_len
    return (left_depth, right_depth) if left_max else (right_depth, left_depth)


  def __last_unary(self, depth: list[Node]) -> bool:
    return len(depth) > 1 and isinstance(depth[-2], UnaryOperatorNode)
