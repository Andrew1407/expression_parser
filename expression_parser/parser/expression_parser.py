from .tokens import Token, Operator, TokenType, Signature, SymbolTemplate, functions_args


class ParsingExeprion(Exception):
  def __init__(self, message: str, symbol: str, position: int):
    super().__init__(message.format(symbol=symbol, position=position))
    self.symbol: str = symbol
    self.position: int = position


class ExpressionParser:
  def __init__(self, expression: str):
    self.__expression = expression
    self.__position: int = 0
    self.__tokens: list[Token] = list()
    self.__exceptions: list[ParsingExeprion] = list()

    self.__generate_tokens()
    for t in self.__tokens: t.value = t.value.strip()
    self.__check_last_token()
    self.__define_functions()

  
  def get_tokens(self) -> tuple[Token, ...]:
    return tuple(self.__tokens)

  
  def get_exceptions(self) -> tuple[ParsingExeprion, ...]:
    return tuple(self.__exceptions)

  
  def __generate_tokens(self):
    while self.__position < len(self.__expression):
      match self.__expression[self.__position]:
        case op if Operator.isop(op):
          self.__add_operator_token(op)
        case var if SymbolTemplate.number.match(var):
          self.__add_var_number(var)
        case Signature.FLOAT_POINT:
          self.__add_floating_point()
        case ch if SymbolTemplate.symbol.match(ch):
          self.__add_var_char(ch)
        case Signature.LEFT_PARENTHESIS | Signature.RIGHT_PARENTHESIS as p:
          self.__add_parenthesis(p)
        case space if SymbolTemplate.space.match(space):
          self.__handle_space(space)
        case Signature.DELIMITER:
          self.__add_delimiter()
        case _ as unknown:
          self.__add_exeption('Unknown symbol "{symbol}"', unknown)

      self.__position += 1


  def __get_last_token(self) -> (Token | None):
    return self.__tokens[-1] if len(self.__tokens) else None

  
  def __add_exeption(self, message: str, symbol: str, position: int = -1):
    pos = self.__position if position < 0 else position
    message_full = message + ' at position {position}'
    if not tuple(filter(lambda e: e.position == pos, self.__exceptions)):
      ex = ParsingExeprion(message_full, symbol, pos)
      self.__exceptions.append(ex)


  def __add_operator_token(self, operator: str):
    token = Token.of(operator, TokenType.OPERATOR, self.__position)
    match self.__get_last_token():
      case None if not Operator.isunary(operator):
        self.__add_exeption('Invalid symbol operator "{symbol}"', operator)
      case Token() as t if t.type == TokenType.CONSTANT and t.value.strip() == Signature.FLOAT_POINT:
        self.__add_exeption('Invalid symbol "{symbol}"', operator)
      case Token(type=TokenType.DELIMITER) if not Operator.isunary(operator):
        self.__add_exeption('Invalid symbol "{symbol}"', operator)
      case Token() as t if t.value == '(' and not Operator.isunary(token.value):
        self.__add_exeption('Invalid symbol operator "{symbol}"', operator)
      case Token(type=TokenType.OPERATOR) if not Operator.isunary(token.value):
        self.__add_exeption('Invalid symbol operator "{symbol}"', operator)
    self.__tokens.append(token)


  def __add_var_number(self, variable: str):
    match self.__get_last_token():
      case None:
        token = Token.of(variable, TokenType.CONSTANT, self.__position)
        self.__tokens.append(token)
      case Token() as t if t.type in (TokenType.CONSTANT, TokenType.VARIABLE):
        self.__check_space_entries(variable)
        t.value += variable
        t.end = self.__position
      case Token() as t:
        self.__check_after_lpar(t, variable)
        token = Token.of(variable, TokenType.CONSTANT, self.__position)
        self.__tokens.append(token)


  def __add_floating_point(self):
    match self.__get_last_token():
      case None:
        new_float = Token.of(Signature.FLOAT_POINT, TokenType.CONSTANT, self.__position)
        self.__tokens.append(new_float)
      case Token(type=TokenType.VARIABLE) as t:
        self.__add_exeption('Unexpected symbol "{symbol}"', Signature.FLOAT_POINT)
        t.value += Signature.FLOAT_POINT
        t.end = self.__position
      case Token() as t if t.type != TokenType.CONSTANT:
        self.__check_after_lpar(t, Signature.FLOAT_POINT)
        new_float = Token.of(Signature.FLOAT_POINT, TokenType.CONSTANT, self.__position)
        self.__tokens.append(new_float)
      case Token(type, value) as t if type == TokenType.CONSTANT and Signature.FLOAT_POINT in value:
        self.__add_exeption('Invalid symbol "{symbol}"', Signature.FLOAT_POINT)
        t.value += Signature.FLOAT_POINT
        t.end = self.__position
      case Token() as t:
        self.__check_space_entries(Signature.FLOAT_POINT)
        t.value += Signature.FLOAT_POINT
        t.end = self.__position


  def __add_var_char(self, ch: str):
    match self.__get_last_token():
      case None:
        token = Token.of(ch, TokenType.VARIABLE, self.__position)
        self.__tokens.append(token)
      case Token(type=TokenType.VARIABLE) as t:
        self.__check_space_entries(ch)
        t.value += ch
        t.end = self.__position
      case Token(type=TokenType.CONSTANT) as t:
        if SymbolTemplate.numbers_range.match(t.value):
          self.__add_exeption('Invalid symbol "{symbol}"', ch)
        self.__check_space_entries(ch)
        t.value += ch
        t.end = self.__position
        t.type = TokenType.VARIABLE
      case Token() as t:
        self.__check_after_lpar(t, ch)
        token = Token.of(ch, TokenType.VARIABLE, self.__position)
        self.__tokens.append(token)


  def __add_parenthesis(self, parenthesis: str):
    generated = Token.of(parenthesis, TokenType.PARENTHESIS, self.__position)
    token = self.__get_last_token()
    match parenthesis:
      case Signature.LEFT_PARENTHESIS:
        if token and (token.type == TokenType.CONSTANT or token.value == Signature.RIGHT_PARENTHESIS):
          self.__add_exeption('Unexpected left parenthesis "{symbol}"', Signature.LEFT_PARENTHESIS)
        self.__tokens.append(generated)
      case Signature.RIGHT_PARENTHESIS:
        if not token:
          self.__add_exeption('Unexpected right parenthesis', Signature.RIGHT_PARENTHESIS)
        elif token.type == TokenType.OPERATOR:
          self.__add_exeption('Unexpected symbol "{symbol}"', parenthesis)
        elif token.type == TokenType.CONSTANT and token.value.strip() == Signature.FLOAT_POINT:
          self.__add_exeption('Invalid symbol "{symbol}"', parenthesis)
        elif token.type == TokenType.DELIMITER:
          self.__add_exeption('Unexpected symbol "{symbol}"', parenthesis)
        self.__tokens.append(generated)


  def __add_delimiter(self):
    generated = Token.of(Signature.DELIMITER, TokenType.DELIMITER, self.__position)
    match self.__get_last_token():
      case None:
        self.__add_exeption('Unexpected delimiter symbol "{symbol}"', Signature.DELIMITER)
      case Token() as t if t.type == TokenType.OPERATOR or t.value.strip() in (Signature.FLOAT_POINT, Signature.LEFT_PARENTHESIS):
        self.__add_exeption('Unexpected delimiter symbol "{symbol}"', Signature.DELIMITER)
      case Token(type=TokenType.DELIMITER):
        self.__add_exeption('Unexpected delimiter symbol "{symbol}"', Signature.DELIMITER)
    self.__tokens.append(generated)


  def __handle_space(self, space: str):
    match self.__get_last_token():
      case Token() as t if t.type in (TokenType.CONSTANT, TokenType.VARIABLE):
        t.value += space


  def __check_space_entries(self, value: str):
    previous = self.__expression[self.__position - 1]
    if SymbolTemplate.space.match(previous):
      self.__add_exeption('Unexpected symbol "{symbol}"', value)


  def __check_after_lpar(self, token: Token, value: str):
    if token.type == TokenType.PARENTHESIS and token.value == Signature.RIGHT_PARENTHESIS:
      self.__add_exeption('Unexpected symbol "{symbol}"', value)


  def __check_last_token(self):
    match self.__get_last_token():
      case Token() as t if t.type == TokenType.CONSTANT and t.value.strip() == Signature.FLOAT_POINT:
        position = self.__expression.rindex(Signature.FLOAT_POINT)
        self.__add_exeption('Invalid symbol "{symbol}"', t.value, position)
      case Token(type=TokenType.DELIMITER) as t:
        if len(self.__tokens) > 1:
          position = self.__expression.rindex(Signature.DELIMITER)
          self.__add_exeption('Invalid symbol "{symbol}"', t.value, position)
      case Token(type=TokenType.PARENTHESIS, value=Signature.LEFT_PARENTHESIS) as t:
        position = self.__expression.rindex(t.value)
        self.__add_exeption('Unexpected left parenthesis "{symbol}"', t.value, position)
      case Token() as t if t.type == TokenType.OPERATOR:
        unary = Operator.isunary(t.value)
        if unary or len(self.__tokens) > 1 and not unary:
          position = self.__expression.rindex(t.value)
          self.__add_exeption('Unexpected symbol "{symbol}"', t.value, position)


  def __define_functions(self):
    for t in self.__tokens:
      if t.value in functions_args: t.type = TokenType.FUNCTION
