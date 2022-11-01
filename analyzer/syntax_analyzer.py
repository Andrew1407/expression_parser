from typing import Iterable
from types import NoneType
from parser.tokens import Token, TokenType, Operator, Signature
from .tree_nodes import *


class SyntaxAnalyzer:
  def __init__(self, tokens: Iterable[Token]):
    self.__position: int = 0
    self.__tokens: tuple[Token] = tuple(tokens)
    self.__tree: Node = None

    self.__analyze()


  def get_tree(self) -> Node:
    return self.__tree


  def __analyze(self):
    self.__tree = self.__build_additive_node()


  def __get_current_token(self, next: bool=False) -> (Token | NoneType):
    token = self.__tokens[self.__position] if self.__position < len(self.__tokens) else None
    if next: self.__position += 1
    return token


  def __build_additive_node(self) -> Node:
    left = self.__build_multiplicative_node()
    token = self.__get_current_token()
    while token and token.value in (Operator.PLUS.value, Operator.MINUS.value):
      token = self.__get_current_token(next=True)
      left = BinaryOperatorNode(value=token, left=left, right=self.__build_multiplicative_node())
      token = self.__get_current_token()
    return left


  def __build_multiplicative_node(self) -> Node:
    left = self.__build_unary_operator_node()
    token = self.__get_current_token()
    while token and token.type == TokenType.OPERATOR and not Operator.isunary(token.value):
      token = self.__get_current_token(next=True)
      left = BinaryOperatorNode(value=token, left=left, right=self.__build_unary_operator_node())
      token = self.__get_current_token()
    return left


  def __build_unary_operator_node(self) -> Node:
    token = self.__get_current_token()
    expression: (Node | NoneType) = None
    if token and Operator.isunary(token.value):
      token = self.__get_current_token(next=True)
      expression = self.__build_unary_operator_node()
      return UnaryOperatorNode(value=token, expression=expression)
    return self.__build_primary_node()


  def __build_primary_node(self) -> Node:
    token = self.__get_current_token()
    if token and token.type in (TokenType.VARIABLE, TokenType.FUNCTION):
      token = self.__get_current_token(next=True)
      token_next = self.__get_current_token()
      if token_next and token_next.value == Signature.LEFT_PARENTHESIS:
        return self.__build_function_node(token)
      else:
        return Node(value=token)
    
    if token and token.type == TokenType.CONSTANT:
      token = self.__get_current_token(next=True)
      return Node(value=token)

    if token and token.value == Signature.LEFT_PARENTHESIS:
      lp = self.__get_current_token(next=True)
      expression = self.__build_additive_node()
      token = self.__get_current_token(next=True)
      if not (token and token.value == Signature.RIGHT_PARENTHESIS):
        raise Exception(f'no right parenthesis found for: "{lp}"; expecting "{Signature.RIGHT_PARENTHESIS}"')
      return Node(value=expression)

    raise Exception(f'nonparsable token: {token}')


  def __build_function_node(self, fn: Token) -> Node:
    token = self.__get_current_token(next=True)
    args: list[Node] = list()
    if not (token and token.value == Signature.LEFT_PARENTHESIS):
      raise Exception(f'function call (left parenthesis) expected for: "{fn}"')
    if not (token and token.value == Signature.RIGHT_PARENTHESIS):
      args = self.__get_function_args()
    token = self.__get_current_token(next=True)
    if not (token and token.value == Signature.RIGHT_PARENTHESIS):
      raise Exception(f'right parenthesis expected for: "{fn}"')
    return FunctionNode(value=fn, args=args)


  def __get_function_args(self) -> tuple[Node]:
    token: (Token | NoneType) = None
    expression: (Node | NoneType) = None
    args: list[Node] = list()
    while True:
      expression = self.__build_additive_node()
      if not expression: break
      args.append(expression)
      token = self.__get_current_token()
      if not (token and token.type == TokenType.DELIMITER):
        break
      self.__get_current_token(next=True)
    return args
