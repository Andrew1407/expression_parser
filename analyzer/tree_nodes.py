from dataclasses import dataclass
from types import NoneType
from parser.tokens import Token
import json


class SyntaxAnalysisException(Exception): ...


@dataclass
class Node:
  value: Token

  def to_json(self):
    entries = dict(type=self.__class__.__name__) | self.__dict__
    return json.dumps(entries, default=lambda o: dict(type=o.__class__.__name__) | o.__dict__, indent=2)


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