from enum import Enum
from dataclasses import dataclass
import re


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


@dataclass
class Token:
  type: TokenType
  value: str


class ExpressionParser:
  def __init__(self, expression: str):
    self.__expression = expression
    self.__position: int = 0
    self.__tokens: list[Token] = list()
    self.__exceptions: list[Exception] = list()

    self.__generate_tokens()
    for t in self.__tokens: t.value = t.value.strip()
    self.__check_last_token()


  
  def get_tokens(self) -> list[Token]:
    return self.__tokens

  
  def get_exceptions(self) -> list[Exception]:
    return self.__exceptions

  
  def __generate_tokens(self):
    while self.__position < len(self.__expression):
      match self.__expression[self.__position]:
        case op if Operator.isop(op):
          self.__add_operator_token(op)
        case var if re.match(r'\d', var):
          self.__add_var_number(var)
        case '.' as fp:
          self.__add_floating_point(fp)
        case ch if re.match(r'[A-Za-z|_]', ch):
          self.__add_var_char(ch)
        case '(' | ')' as p:
          self.__add_parenthesis(p)
        case space if re.match(r'\s', space):
          self.__handle_space(space)
        case _ as unknown:
          ex = Exception(f'unknown symbol "{unknown}" at position {self.__position}')
          self.__exceptions.append(ex)

      self.__position += 1


  def __get_last_token(self):
    return self.__tokens[-1] if len(self.__tokens) else None


  def __add_operator_token(self, operator: str):
    token = Token(value=operator, type=TokenType.OPERATOR)
    match self.__get_last_token():
      case None if not Operator.isunary(operator):
        ex = Exception(f'invalid symbol operator "{operator}" at position {self.__position}')
        self.__exceptions.append(ex)
      case Token() as t if t.type == TokenType.CONSTANT and t.value.strip() == '.':
        ex = Exception(f'invalid symbol "{operator}" at position {self.__position}')
        self.__exceptions.append(ex)
      case Token() as t if t.value == '(' and not Operator.isunary(token.value):
        ex = Exception(f'invalid symbol operator "{operator}" at position {self.__position}')
        self.__exceptions.append(ex)
    self.__tokens.append(token)


  def __add_var_number(self, variable: str):
    match self.__get_last_token():
      case None:
        token = Token(value=variable, type=TokenType.CONSTANT)
        self.__tokens.append(token)
      case Token() as t if t.type in (TokenType.CONSTANT, TokenType.VARIABLE):
        self.__check_space_entries(variable)
        t.value += variable
      case Token() as t:
        self.__check_after_lpar(t, variable)
        token = Token(value=variable, type=TokenType.CONSTANT)
        self.__tokens.append(token)
    

  def __add_floating_point(self, symbol: str):
    match self.__get_last_token():
      case None:
        new_float = Token(value=symbol, type=TokenType.CONSTANT)
        self.__tokens.append(new_float)
      case Token(type=TokenType.VARIABLE) as t:
        ex = Exception(f'uhexpected symbol "{symbol}" at position {self.__position}')
        self.__exceptions.append(ex)
        t.value += symbol
      case Token() as t if t.type != TokenType.CONSTANT:
        self.__check_after_lpar(t, symbol)
        new_float = Token(value=symbol, type=TokenType.CONSTANT)
        self.__tokens.append(new_float)
      case Token(type, value) as t if type == TokenType.CONSTANT and symbol in value:
        ex = Exception(f'invalid symbol "{symbol}" at position {self.__position}')
        self.__exceptions.append(ex)
        t.value += symbol
      case Token() as t:
        self.__check_space_entries(symbol)
        t.value += symbol


  def __add_var_char(self, ch: str):
    match self.__get_last_token():
      case None:
        token = Token(value=ch, type=TokenType.VARIABLE)
        self.__tokens.append(token)
      case Token(type=TokenType.VARIABLE) as t:
        self.__check_space_entries(ch)
        t.value += ch
      case Token(type=TokenType.CONSTANT) as t:
        self.__check_space_entries(ch)
        t.value += ch
        t.type = TokenType.VARIABLE
      case Token() as t:
        if re.match(r'^[\d\.]+$', t.value):
          ex = Exception(f'invalid symbol "{ch}" at position {self.__position}')
          self.__exceptions.append(ex)
        self.__check_after_lpar(t, ch)
        token = Token(value=ch, type=TokenType.VARIABLE)
        self.__tokens.append(token)


  def __add_parenthesis(self, parenthesis: str):
    generated = Token(value=parenthesis, type=TokenType.PARENTHESIS)
    token = self.__get_last_token()
    match parenthesis:
      case '(':
        if token and token.type == TokenType.CONSTANT:
          ex = Exception(f'unexpected left parenthesis at position {self.__position}')
          self.__exceptions.append(ex)
        self.__tokens.append(generated)
      case ')':
        ex = None
        if not token:
          ex = Exception(f'unexpected right parenthesis at position {self.__position}')
        elif token.type == TokenType.OPERATOR:
          ex = Exception(f'unexpected symbol "{parenthesis}" at position {self.__position}')
        elif token.type == TokenType.CONSTANT and token.value.strip() == '.':
          ex = Exception(f'invalid symbol "{parenthesis}" at position {self.__position}')

        if ex: self.__exceptions.append(ex)
        self.__tokens.append(generated)


  def __handle_space(self, space: str):
    match self.__get_last_token():
      case Token() as t if t.type in (TokenType.CONSTANT, TokenType.VARIABLE):
        t.value += space


  def __check_space_entries(self, value: str):
    previous = self.__expression[self.__position - 1]
    if re.match(r'\s', previous):
      ex = Exception(f'unexpected symbol "{value}" at position {self.__position}')
      self.__exceptions.append(ex)

  
  def __check_after_lpar(self, token: Token, value: str):
    if token.type == TokenType.PARENTHESIS and token.value == ')':
      ex = Exception(f'unexpected symbol "{value}" at position {self.__position}')
      self.__exceptions.append(ex)
  

  def __check_last_token(self):
    token = self.__get_last_token()
    match self.__get_last_token():
      case Token() as t if t.type == TokenType.CONSTANT and t.value.strip() == '.':
        position = self.__expression.rindex('.')
        ex = Exception(f'invalid symbol "{token.value}" at position {position}')
        self.__exceptions.append(ex)
      case Token() as t if t.type == TokenType.OPERATOR:
        position = self.__expression.rindex(t.value)
        ex = Exception(f'unexpected symbol "{t.value}" at position {position}')
        self.__exceptions.append(ex)
