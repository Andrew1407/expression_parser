from dataclasses import dataclass
from types import NoneType
from parser.tokens import Token


@dataclass
class Node:
  value: Token


@dataclass
class UnaryOperatorNode(Node):
  expression: (Node | NoneType)


@dataclass
class BinaryOperatorNode(Node):
  left: (Node | NoneType)
  right: (Node | NoneType)


@dataclass
class FunctionNode(Node):
  args: tuple[Node]
