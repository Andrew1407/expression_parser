from copy import deepcopy
from types import NoneType
from parser.tokens import Token, TokenType, Operator
from analyzer.tree_nodes import Node, FunctionNode, UnaryOperatorNode, BinaryOperatorNode


def minimize_redundant_nodes(node: Node) -> Node:
  match node:
    case BinaryOperatorNode(value=(Token(value=Operator.MINUS.value))) if node.left.value.value == node.right.value.value:
      return Node(value=Token.of('0', TokenType.CONSTANT, node.value.start))
    case BinaryOperatorNode() if node.value.value in (Operator.PLUS.value, Operator.MINUS.value) and node.left.value.value == '0':
      return minimize_redundant_nodes(node.right)
    case BinaryOperatorNode() if node.value.value in (Operator.PLUS.value, Operator.MINUS.value) and node.right.value.value == '0':
      return minimize_redundant_nodes(node.left)
    case BinaryOperatorNode(value=(Token(value=Operator.MULTIPLY.value))) if node.left.value.value == '1':
      return minimize_redundant_nodes(node.right)
    case BinaryOperatorNode(value=(Token(value=Operator.MULTIPLY.value))) if node.right.value.value == '1':
      return minimize_redundant_nodes(node.left)
    case BinaryOperatorNode(value=(Token(value=Operator.MULTIPLY.value))) if node.left.value.value == '0':
      return node.left
    case BinaryOperatorNode(value=(Token(value=Operator.MULTIPLY.value))) if node.right.value.value == '0':
      return node.right
    case BinaryOperatorNode(value=(Token(value=Operator.DIVIDE.value))) if node.left.value.value == node.right.value.value:
      return Node(value=Token.of('1', TokenType.CONSTANT, node.value.start))
    case BinaryOperatorNode(value=(Token(value=Operator.DIVIDE.value))) if node.right.value.value == '1':
      return minimize_redundant_nodes(node.left)
    case BinaryOperatorNode(value=(Token(value=Operator.DIVIDE.value))) if node.left.value.value == '0':
      return node.left
    case UnaryOperatorNode() if node.expression.value.value == '0':
      return node.expression
    case UnaryOperatorNode():
      node.expression = minimize_redundant_nodes(node.expression)
      return node.expression if node.expression.value.value == '0' else node
    case BinaryOperatorNode():
      left = node.left.value
      right = node.right.value
      node.left = minimize_redundant_nodes(node.left)
      node.right = minimize_redundant_nodes(node.right)
      minimized = left != node.left.value or right != node.right.value
      return minimize_redundant_nodes(node) if minimized else node
    case FunctionNode():
      node.args = tuple(minimize_redundant_nodes(arg) for arg in node.args)
      return node
    case Node():
      return node
    case _:
      return minimize_redundant_nodes(node)


def convert_to_primitive(node: Node):
  match node:
    case BinaryOperatorNode(value=(Token(value=Operator.MINUS.value))) as minus:
      convert_to_primitive(minus.left)
      convert_to_primitive(minus.right)
      right_wrapper = Token.of(Operator.MINUS.value, TokenType.OPERATOR, minus.right.value.start)
      minus.value.value = Operator.PLUS.value
      minus.right = UnaryOperatorNode(value=right_wrapper, expression=minus.right)
    case BinaryOperatorNode(value=(Token(value=Operator.DIVIDE.value))) as division:
      convert_to_primitive(division.left)
      convert_to_primitive(division.right)
      right_leaf_start = division.right.value.start
      one_constant = Token.of('1', TokenType.CONSTANT, right_leaf_start)
      division_by_one = Token.of(Operator.DIVIDE.value, TokenType.OPERATOR, right_leaf_start)
      division.value.value = Operator.MULTIPLY.value
      division.right = BinaryOperatorNode(value=division_by_one, left=Node(one_constant), right=division.right)
    case BinaryOperatorNode() as operation if operation.value.value in (Operator.PLUS.value, Operator.MULTIPLY.value, Operator.POWER.value):
      convert_to_primitive(operation.left)
      convert_to_primitive(operation.right)
    case UnaryOperatorNode() as unary:
      convert_to_primitive(unary.expression)
    case FunctionNode() as function:
      for expression in function.args:
        convert_to_primitive(expression)


def reduce_unaries(node: Node):
  match node:
    case BinaryOperatorNode() as binary:
      for key in ('left', 'right'):
        leaf = getattr(binary, key)
        expression, unary = get_unary_min_depth(leaf)
        if unary: unary.expression = expression
        setattr(binary, key, unary if unary else expression)
        reduce_unaries(expression)
    case FunctionNode() as function:
      args = list(function.args)
      for i in range(len(args)):
        arg = args[i]
        expression, unary = get_unary_min_depth(arg)
        if unary: unary.expression = expression
        args[i] = unary if unary else expression
        reduce_unaries(expression)
      function.args = tuple(args)


def get_unary_min_depth(node: Node) -> tuple[Node, (UnaryOperatorNode | NoneType)]:
  if not isinstance(node, UnaryOperatorNode):
    return node, None
  unary = node
  minus: bool = unary.value.value == Operator.MINUS.value
  current_node = node
  while True:
    current_node = current_node.expression
    if not isinstance(current_node, UnaryOperatorNode): break
    if current_node.value.value == Operator.MINUS.value:
      minus = not minus
      unary = current_node
  if not minus: unary = None
  return current_node, unary


def open_brackets(node: Node) -> Node:
  match node:
    case UnaryOperatorNode():
      expression = node.expression
      node = apply_minus(expression)
    case BinaryOperatorNode():
      node.left = open_brackets(node.left)
      node.right = open_brackets(node.right)
    case FunctionNode():
      node.args = tuple(open_brackets(expr) for expr in node.args)
  return node
        

def apply_minus(node: Node) -> Node:
  match node:
    case UnaryOperatorNode():
      node = open_brackets(node.expression)
    case BinaryOperatorNode(value=(Token(value=Operator.PLUS.value))):
      node.left = apply_minus(open_brackets(node.left))
      node.right = apply_minus(open_brackets(node.right))
    case BinaryOperatorNode() if node.value.value in (Operator.MULTIPLY.value, Operator.DIVIDE.value):
      node.left = open_brackets(node.left)
      node.right = open_brackets(node.right)
      if node.left.value.value != '1':
        node.left = apply_minus(node.left)
      else:
        node.right = apply_minus(node.right)
    case Node():
      node = UnaryOperatorNode(
        value=Token.of(Operator.MINUS.value, TokenType.OPERATOR, node.value.start),
        expression=open_brackets(node),
      )
  return node


def convert_to_optimized(node: Node):
  match node:
    case FunctionNode() as function:
      for expression in function.args:
        convert_to_optimized(expression)
    case BinaryOperatorNode(value=(Token(value=Operator.POWER.value))) as power:
      convert_to_optimized(power.left)
      convert_to_optimized(power.right)
    case BinaryOperatorNode(value=(Token(value=Operator.PLUS.value))) as plus:
      convert_to_optimized(plus.left)
      convert_to_optimized(plus.right)
      left_minus = isinstance(plus.left, UnaryOperatorNode)
      right_minus = isinstance(plus.right, UnaryOperatorNode)
      if right_minus:
        plus.value.value = Operator.MINUS.value
        plus.right = plus.right.expression
      elif left_minus:
        plus.value.value = Operator.MINUS.value
        left = plus.left.expression
        plus.left = plus.right
        plus.right = left
    case BinaryOperatorNode(value=(Token(value=Operator.MULTIPLY.value))) as multiplication:
      convert_to_optimized(multiplication.left)
      convert_to_optimized(multiplication.right)
      left_denominator = __get_denominator(multiplication.left)
      right_denominator = __get_denominator(multiplication.right)
      if left_denominator and not right_denominator:
        multiplication.value.value = Operator.DIVIDE.value
        multiplication.right = multiplication.left
        multiplication.left = right_denominator
        __remove_redundant_minuses(multiplication)
      elif not left_denominator and right_denominator:
        multiplication.value.value = Operator.DIVIDE.value
        multiplication.right = right_denominator
        __remove_redundant_minuses(multiplication)
      elif left_denominator and right_denominator:
        denominator_operator = deepcopy(multiplication.value)
        multiplication.value.value = Operator.DIVIDE.value
        multiplication.left = multiplication.left.left
        multiplication.right = BinaryOperatorNode(
          value=denominator_operator,
          left=left_denominator,
          right=right_denominator,
        )
        __remove_redundant_minuses(multiplication.right)


# utils

def __get_denominator(node: BinaryOperatorNode) -> (Node | NoneType):
  if node.value.value != Operator.DIVIDE.value: return None
  if node.left.value.value != '1': return None
  return node.right


def __remove_redundant_minuses(node: BinaryOperatorNode):
  if isinstance(node.left, UnaryOperatorNode) and isinstance(node.right, UnaryOperatorNode):
    node.right = node.right.expression
    node.left = node.left.expression
