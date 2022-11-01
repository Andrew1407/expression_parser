from enum import Enum
from dataclasses import dataclass
import re


class Signature:
  DELIMITER: str = ','
  FLOAT_POINT: str = '.'
  LEFT_PARENTHESIS: str = '('
  RIGHT_PARENTHESIS: str = ')'


class SymbolTemplate:
  number: re.Pattern = re.compile(r'\d')
  symbol: re.Pattern = re.compile(r'[A-Za-z|_]')
  space: re.Pattern = re.compile(r'\s')
  numbers_range: re.Pattern = re.compile(r'^[\d\.]+$')


functions_args: dict[str, int] = dict(
  sin=1,
  rand=0,
  max=2,
  min=2,
  pow=2,
)


class Operator(Enum):
  PLUS = '+'
  MINUS = '-'
  MULTIPLY = '*'
  DIVIDE = '/'
  POWER = '^'

  @staticmethod
  def isop(value: str) -> bool:
    return value in set(e.value for e in set(Operator))


  @staticmethod
  def isunary(value: str) -> bool:
    return value in set(e.value for e in (Operator.PLUS, Operator.MINUS))


class TokenType(Enum):
  PARENTHESIS = 1
  OPERATOR = 2
  FUNCTION = 3
  VARIABLE = 4
  CONSTANT = 5
  DELIMITER = 6


@dataclass
class Token:
  type: TokenType
  value: str
  start: int
  end: int

  def __repr__(self) -> str:
    return f'| type: {self.type.name} | value: \'{self.value}\' | start: {self.start} | end: {self.end} |'

  
  @staticmethod
  def of(value: str, type: TokenType, position: int=0):
    return Token(type, value, position, position)
