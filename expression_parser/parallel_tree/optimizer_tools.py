from copy import deepcopy
from types import NoneType
from expression_parser.parser.tokens import Token, TokenType, Operator
from expression_parser.analyzer.tree_nodes import Node, FunctionNode, UnaryOperatorNode, BinaryOperatorNode


def minimize_redundant_nodes(node: Node) -> Node:
  match node:
    case BinaryOperatorNode(value=(Token(value=Operator.MINUS.value))) if __is_primitive(node.left) and __vals_eq(node.left, node.right):
      return Node(value=Token.of('0', TokenType.CONSTANT, node.value.start))
    case BinaryOperatorNode(value=(Token(value=Operator.PLUS.value))) if __vals_eq(node.left, '0'):
      return minimize_redundant_nodes(node.right)
    case BinaryOperatorNode(value=(Token(value=Operator.MINUS.value))) if __vals_eq(node.left, '0'):
      token = Token.of(Operator.MINUS.value, TokenType.OPERATOR, node.value.start)
      unary = UnaryOperatorNode(value=token, expression=node.right)
      return minimize_redundant_nodes(unary)
    case BinaryOperatorNode() if node.value.value in (Operator.PLUS.value, Operator.MINUS.value) and __vals_eq(node.right, '0'):
      return minimize_redundant_nodes(node.left)
    case BinaryOperatorNode(value=(Token(value=Operator.MULTIPLY.value))) if __vals_eq(node.left, '1'):
      return minimize_redundant_nodes(node.right)
    case BinaryOperatorNode(value=(Token(value=Operator.MULTIPLY.value))) if __vals_eq(node.right, '1'):
      return minimize_redundant_nodes(node.left)
    case BinaryOperatorNode(value=(Token(value=Operator.MULTIPLY.value))) if __vals_eq(node.left, '0'):
      return node.left
    case BinaryOperatorNode(value=(Token(value=Operator.MULTIPLY.value))) if __vals_eq(node.right,'0'):
      return node.right
    case BinaryOperatorNode(value=(Token(value=Operator.DIVIDE.value))) if __vals_eq(node.right, '1'):
      return minimize_redundant_nodes(node.left)
    case BinaryOperatorNode(value=(Token(value=Operator.DIVIDE.value))) if __vals_eq(node.left, '0'):
      return node if __vals_eq(node.right, '0') else node.left
    case UnaryOperatorNode() if __vals_eq(node.expression, '0'):
      return node.expression
    case UnaryOperatorNode():
      node.expression = minimize_redundant_nodes(node.expression)
      return node.expression if __vals_eq(node.expression, '0') else node
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
    case Node() if node.value.type in (TokenType.CONSTANT, TokenType.VARIABLE):
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
    case BinaryOperatorNode(value=(Token(value=Operator.MINUS.value))):
      node.value.value = Operator.PLUS.value
      node.left = open_brackets(node.left)
      node.right = apply_minus(node.right)
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
    case BinaryOperatorNode(value=(Token(value=Operator.MINUS.value))):
      node.value.value = Operator.PLUS.value
    case BinaryOperatorNode(value=(Token(value=Operator.PLUS.value))):
      node.left = apply_minus(open_brackets(node.left))
      node.right = apply_minus(open_brackets(node.right))
    case BinaryOperatorNode() if node.value.value in (Operator.MULTIPLY.value, Operator.DIVIDE.value):
      node.left = open_brackets(node.left)
      node.right = open_brackets(node.right)
      leaf_minus = 'right' if __vals_eq(node.left, '1') else 'left'
      setattr(node, leaf_minus, apply_minus(getattr(node, leaf_minus)))
    case Node():
      node = UnaryOperatorNode(
        value=Token.of(Operator.MINUS.value, TokenType.OPERATOR, node.value.start),
        expression=open_brackets(node),
      )
  return node


def convert_to_optimized(node: Node) -> Node:
  match node:
    case FunctionNode():
      node.args = tuple(convert_to_optimized(arg) for arg in node.args)
    case BinaryOperatorNode(value=(Token(value=Operator.POWER.value))):
      node.left = convert_to_optimized(node.left)
      node.right = convert_to_optimized(node.right)
    case BinaryOperatorNode(value=(Token(value=Operator.PLUS.value))):
      node.left = convert_to_optimized(node.left)
      node.right = convert_to_optimized(node.right)
      left_minus = isinstance(node.left, UnaryOperatorNode)
      right_minus = isinstance(node.right, UnaryOperatorNode)
      if left_minus and right_minus:
        node.left = node.left.expression
        node.right = node.right.expression
        node = UnaryOperatorNode(
          value=Token.of(Operator.MINUS.value, TokenType.OPERATOR, node.value.start),
          expression=node,
        )
      elif right_minus and not left_minus:
        node.value.value = Operator.MINUS.value
        node.right = node.right.expression
      elif left_minus and not right_minus:
        node.value.value = Operator.MINUS.value
        left = node.left.expression
        node.left = node.right
        node.right = left
    case BinaryOperatorNode(value=(Token(value=Operator.MULTIPLY.value))):
      node.left = convert_to_optimized(node.left)
      node.right = convert_to_optimized(node.right)
      left_denominator = __get_denominator(node.left)
      right_denominator = __get_denominator(node.right)
      if left_denominator and not right_denominator:
        node.value.value = Operator.DIVIDE.value
        node.left = node.right
        node.right = left_denominator
        node = __remove_redundant_minuses(node)
      elif not left_denominator and right_denominator:
        node.value.value = Operator.DIVIDE.value
        node.right = convert_to_optimized(right_denominator)
        node = __remove_redundant_minuses(node)
      elif left_denominator and right_denominator:
        denominator_operator = deepcopy(node.value)
        node.value.value = Operator.DIVIDE.value
        node.left = node.left.left
        node.right = BinaryOperatorNode(
          value=denominator_operator,
          left=left_denominator,
          right=right_denominator,
        )
        node.right = __remove_redundant_minuses(node.right)
      else:
        node = __remove_redundant_minuses(node)
  return node


# utils

def __get_denominator(node: BinaryOperatorNode) -> (Node | NoneType):
  if not __vals_eq(node, Operator.DIVIDE.value): return None
  if not __vals_eq(node.left, '1'): return None
  return node.right


def __remove_redundant_minuses(node: BinaryOperatorNode) -> Node:
  unary_left = isinstance(node.left, UnaryOperatorNode)
  unary_right = isinstance(node.right, UnaryOperatorNode)
  if unary_left:
    node.left = node.left.expression
  if unary_right:
    node.right = node.right.expression
  if unary_left and not unary_right or unary_right and not unary_left:
    return UnaryOperatorNode(
      value=Token.of(Operator.MINUS.value, TokenType.OPERATOR, node.value.start),
      expression=node,
    )
  return node


def __is_primitive(node: Node) -> bool:
  return node.value.type in (TokenType.CONSTANT, TokenType.VARIABLE)


def __vals_eq(a: Node | str, b: Node | str) -> bool:
  a = a.value.value if isinstance(a, Node) else a
  b = b.value.value if isinstance(b, Node) else b
  return a == b
