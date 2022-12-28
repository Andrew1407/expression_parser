from dataclasses import dataclass
from types import NoneType
from expression_parser.parser.tokens import Token
import json



@dataclass
class Node:
  value: Token

  def to_json(self):
    parse = lambda o: dict(type=o.__class__.__name__) | o.__dict__
    return json.dumps(parse(self), default=parse, indent=2)


NodesTuple = tuple[Node, ...]

@dataclass
class UnaryOperatorNode(Node):
  expression: (Node | NoneType)


@dataclass
class BinaryOperatorNode(Node):
  left: (Node | NoneType)
  right: (Node | NoneType)


@dataclass
class FunctionNode(Node):
  args: NodesTuple


