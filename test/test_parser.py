import unittest
from expression_parser.parser.expression_parser import ExpressionParser
from expression_parser.parser.tokens import Token, Operator, TokenType, Signature


class TestExpressionParser(unittest.TestCase):
  def test_empty_input(self):
    expression_parser = ExpressionParser(expression=str())
    self.assertTupleEqual(tuple(), expression_parser.get_exceptions())
    self.assertTupleEqual(tuple(), expression_parser.get_tokens())


  def test_nesting_valid(self):
    expression = '(a/(b*c)^45)/-sin(206.6+-(-+(-(val_))^const))'
    expression_parser = ExpressionParser(expression)
    position = iter(range(len(expression) + 1))
    def skip(n):
      for _ in range(max(n - 1, 0)): next(position)
      return next(position)
    expected = (
      Token.of(Signature.LEFT_PARENTHESIS, TokenType.PARENTHESIS, next(position)),
      Token.of('a', TokenType.VARIABLE, next(position)),
      Token.of(Operator.DIVIDE.value, TokenType.OPERATOR, next(position)),
      Token.of(Signature.LEFT_PARENTHESIS, TokenType.PARENTHESIS, next(position)),
      Token.of('b', TokenType.VARIABLE, next(position)),
      Token.of(Operator.MULTIPLY.value, TokenType.OPERATOR, next(position)),
      Token.of('c', TokenType.VARIABLE, next(position)),
      Token.of(Signature.RIGHT_PARENTHESIS, TokenType.PARENTHESIS, next(position)),
      Token.of(Operator.POWER.value, TokenType.OPERATOR, next(position)),
      Token(value='45', type=TokenType.CONSTANT, start=next(position), end=next(position)),
      Token.of(Signature.RIGHT_PARENTHESIS, TokenType.PARENTHESIS, next(position)),
      Token.of(Operator.DIVIDE.value, TokenType.OPERATOR, next(position)),
      Token.of(Operator.MINUS.value, TokenType.OPERATOR, next(position)),
      Token(value='sin', type=TokenType.FUNCTION, start=next(position), end=skip(2)),
      Token.of(Signature.LEFT_PARENTHESIS, TokenType.PARENTHESIS, next(position)),
      Token(value='206.6', type=TokenType.CONSTANT, start=next(position), end=skip(4)),
      Token.of(Operator.PLUS.value, TokenType.OPERATOR, next(position)),
      Token.of(Operator.MINUS.value, TokenType.OPERATOR, next(position)),
      Token.of(Signature.LEFT_PARENTHESIS, TokenType.PARENTHESIS, next(position)),
      Token.of(Operator.MINUS.value, TokenType.OPERATOR, next(position)),
      Token.of(Operator.PLUS.value, TokenType.OPERATOR, next(position)),
      Token.of(Signature.LEFT_PARENTHESIS, TokenType.PARENTHESIS, next(position)),
      Token.of(Operator.MINUS.value, TokenType.OPERATOR, next(position)),
      Token.of(Signature.LEFT_PARENTHESIS, TokenType.PARENTHESIS, next(position)),
      Token(value='val_', type=TokenType.VARIABLE, start=next(position), end=skip(3)),
      Token.of(Signature.RIGHT_PARENTHESIS, TokenType.PARENTHESIS, next(position)),
      Token.of(Signature.RIGHT_PARENTHESIS, TokenType.PARENTHESIS, next(position)),
      Token.of(Operator.POWER.value, TokenType.OPERATOR, next(position)),
      Token(value='const', type=TokenType.VARIABLE, start=next(position), end=skip(4)),
      Token.of(Signature.RIGHT_PARENTHESIS, TokenType.PARENTHESIS, next(position)),
      Token.of(Signature.RIGHT_PARENTHESIS, TokenType.PARENTHESIS, next(position)),
    )
    self.assertTupleEqual(tuple(), expression_parser.get_exceptions())
    self.assertTupleEqual(expected, expression_parser.get_tokens())
    

  def test_space_skipping(self):
    expression = '  sin\t(\n\n26 ) \n  '
    expression_parser = ExpressionParser(expression)
    expected = (
      Token(value='sin', type=TokenType.FUNCTION, start=2, end=4),
      Token.of(Signature.LEFT_PARENTHESIS, TokenType.PARENTHESIS, 6),
      Token(value='26', type=TokenType.CONSTANT, start=9, end=10),
      Token.of(Signature.RIGHT_PARENTHESIS, TokenType.PARENTHESIS, 12),
    )
    self.assertTupleEqual(tuple(), expression_parser.get_exceptions())
    self.assertTupleEqual(expected, expression_parser.get_tokens())

  
  def test_point_parsing(self):
    expression = '.9 - 2.8 ^ 3. + -.7'
    expression_parser = ExpressionParser(expression)
    expected = (
      Token(value='.9', type=TokenType.CONSTANT, start=0, end=1),
      Token.of(Operator.MINUS.value, TokenType.OPERATOR, 3),
      Token(value='2.8', type=TokenType.CONSTANT, start=5, end=7),
      Token.of(Operator.POWER.value, TokenType.OPERATOR, 9),
      Token(value='3.', type=TokenType.CONSTANT, start=11, end=12),
      Token.of(Operator.PLUS.value, TokenType.OPERATOR, 14),
      Token.of(Operator.MINUS.value, TokenType.OPERATOR, 16),
      Token(value='.7', type=TokenType.CONSTANT, start=17, end=18),
    )
    self.assertTupleEqual(tuple(), expression_parser.get_exceptions())
    self.assertTupleEqual(expected, expression_parser.get_tokens())

  
  def test_invalid_point_symbols_on_start(self):
    expression = ' . '
    expression_parser = ExpressionParser(expression)
    expected_tokens = (
      Token.of(Signature.FLOAT_POINT, TokenType.CONSTANT, 1),
    )
    expected_exceptions = (
      'Invalid symbol "." at position 1',
    )
    result_exception = tuple(str(ex) for ex in expression_parser.get_exceptions())
    self.assertTupleEqual(expected_tokens, expression_parser.get_tokens())
    self.assertEqual(expected_exceptions, result_exception)


  def test_invalid_point_symbols_on_end(self):
    expression = '8 + .'
    expression_parser = ExpressionParser(expression)
    expected_tokens = (
      Token.of('8', TokenType.CONSTANT, 0),
      Token.of(Operator.PLUS.value, TokenType.OPERATOR, 2),
      Token.of(Signature.FLOAT_POINT, TokenType.CONSTANT, 4),
    )
    expected_exceptions = (
      'Invalid symbol "." at position 4',
    )
    result_exception = tuple(str(ex) for ex in expression_parser.get_exceptions())
    self.assertTupleEqual(expected_tokens, expression_parser.get_tokens())
    self.assertEqual(expected_exceptions, result_exception)


  def test_invalid_binary_operatorss_on_start(self):
    mul_parser = ExpressionParser(expression='*8')
    div_parser = ExpressionParser(expression='/8')
    pow_parser = ExpressionParser(expression='^8')

    expected_tokens_mul = (
      Token.of(Operator.MULTIPLY.value, TokenType.OPERATOR, 0),
      Token.of('8', TokenType.CONSTANT, 1),
    )
    expected_tokens_div = (
      Token.of(Operator.DIVIDE.value, TokenType.OPERATOR, 0),
      Token.of('8', TokenType.CONSTANT, 1),
    )
    expected_tokens_pow = (
      Token.of(Operator.POWER.value, TokenType.OPERATOR, 0),
      Token.of('8', TokenType.CONSTANT, 1),
    )

    expected_exceptions_mul = (
      'Invalid symbol operator "*" at position 0',
    )
    expected_exceptions_div = (
      'Invalid symbol operator "/" at position 0',
    )
    expected_exceptions_pow = (
      'Invalid symbol operator "^" at position 0',
    )

    self.assertTupleEqual(expected_tokens_mul, mul_parser.get_tokens())
    self.assertTupleEqual(expected_exceptions_mul, tuple(str(ex) for ex in mul_parser.get_exceptions()))

    self.assertTupleEqual(expected_tokens_div, div_parser.get_tokens())
    self.assertTupleEqual(expected_exceptions_div, tuple(str(ex) for ex in div_parser.get_exceptions()))

    self.assertTupleEqual(expected_tokens_pow, pow_parser.get_tokens())
    self.assertTupleEqual(expected_exceptions_pow, tuple(str(ex) for ex in pow_parser.get_exceptions()))

    
  def test_invalid_binary_operatorss_on_end(self):
    mul_parser = ExpressionParser(expression='8*')
    div_parser = ExpressionParser(expression='8/')
    pow_parser = ExpressionParser(expression='8^')
    minus_parser = ExpressionParser(expression='8-')
    plus_parser = ExpressionParser(expression='8+')

    expected_tokens_mul = (
      Token.of('8', TokenType.CONSTANT, 0),
      Token.of(Operator.MULTIPLY.value, TokenType.OPERATOR, 1),
    )
    expected_tokens_div = (
      Token.of('8', TokenType.CONSTANT, 0),
      Token.of(Operator.DIVIDE.value, TokenType.OPERATOR, 1),
    )
    expected_tokens_pow = (
      Token.of('8', TokenType.CONSTANT, 0),
      Token.of(Operator.POWER.value, TokenType.OPERATOR, 1),
    )
    expected_tokens_minus = (
      Token.of('8', TokenType.CONSTANT, 0),
      Token.of(Operator.MINUS.value, TokenType.OPERATOR, 1),
    )
    expected_tokens_plus = (
      Token.of('8', TokenType.CONSTANT, 0),
      Token.of(Operator.PLUS.value, TokenType.OPERATOR, 1),
    )

    expected_exceptions_mul = (
      'Unexpected symbol "*" at position 1',
    )
    expected_exceptions_div = (
      'Unexpected symbol "/" at position 1',
    )
    expected_exceptions_pow = (
      'Unexpected symbol "^" at position 1',
    )
    expected_exceptions_minus = (
      'Unexpected symbol "-" at position 1',
    )
    expected_exceptions_plus = (
      'Unexpected symbol "+" at position 1',
    )

    self.assertTupleEqual(expected_tokens_mul, mul_parser.get_tokens())
    self.assertTupleEqual(expected_exceptions_mul, tuple(str(ex) for ex in mul_parser.get_exceptions()))

    self.assertTupleEqual(expected_tokens_div, div_parser.get_tokens())
    self.assertTupleEqual(expected_exceptions_div, tuple(str(ex) for ex in div_parser.get_exceptions()))

    self.assertTupleEqual(expected_tokens_pow, pow_parser.get_tokens())
    self.assertTupleEqual(expected_exceptions_pow, tuple(str(ex) for ex in pow_parser.get_exceptions()))

    self.assertTupleEqual(expected_tokens_minus, minus_parser.get_tokens())
    self.assertTupleEqual(expected_exceptions_minus, tuple(str(ex) for ex in minus_parser.get_exceptions()))

    self.assertTupleEqual(expected_tokens_plus, plus_parser.get_tokens())
    self.assertTupleEqual(expected_exceptions_plus, tuple(str(ex) for ex in plus_parser.get_exceptions()))


  def test_parenthesis_at_bounds(self):
    start_parser = ExpressionParser(expression=') - 8')
    end_parser = ExpressionParser(expression='8 - (')

    expected_tokens_start = (
      Token.of(Signature.RIGHT_PARENTHESIS, TokenType.PARENTHESIS, 0),
      Token.of(Operator.MINUS.value, TokenType.OPERATOR, 2),
      Token.of('8', TokenType.CONSTANT, 4),
    )

    expected_tokens_end = (
      Token.of('8', TokenType.CONSTANT, 0),
      Token.of(Operator.MINUS.value, TokenType.OPERATOR, 2),
      Token.of(Signature.LEFT_PARENTHESIS, TokenType.PARENTHESIS, 4),
    )

    expected_exceptions_start = (
      'Unexpected right parenthesis at position 0',
    )
    expected_exceptions_end = (
      'Unexpected left parenthesis "(" at position 4',
    )

    self.assertTupleEqual(expected_tokens_start, start_parser.get_tokens())
    self.assertTupleEqual(expected_exceptions_start, tuple(str(ex) for ex in start_parser.get_exceptions()))

    self.assertTupleEqual(expected_tokens_end, end_parser.get_tokens())
    self.assertTupleEqual(expected_exceptions_end, tuple(str(ex) for ex in end_parser.get_exceptions()))


  def test_spacing_exceptions(self):
    var_parser = ExpressionParser(expression='va riable')
    int_parser = ExpressionParser(expression='83 234')
    float1_parser = ExpressionParser(expression='83. 234')
    float2_parser = ExpressionParser(expression='83 .234')
    float3_parser = ExpressionParser(expression='. 234')
    float4_parser = ExpressionParser(expression='234 .')

    expected_tokens_var = (
      Token(value='va riable', type=TokenType.VARIABLE, start=0, end=8),
    )

    expected_tokens_int = (
      Token(value='83 234', type=TokenType.CONSTANT, start=0, end=5),
    )

    expected_tokens_float1 = (
      Token(value='83. 234', type=TokenType.CONSTANT, start=0, end=6),
    )

    expected_tokens_float2 = (
      Token(value='83 .234', type=TokenType.CONSTANT, start=0, end=6),
    )

    expected_tokens_float3 = (
      Token(value='. 234', type=TokenType.CONSTANT, start=0, end=4),
    )

    expected_tokens_float4 = (
      Token(value='234 .', type=TokenType.CONSTANT, start=0, end=4),
    )

    self.assertTupleEqual(expected_tokens_var, var_parser.get_tokens())
    self.assertTupleEqual(('Unexpected symbol "r" at position 3',), tuple(str(ex) for ex in var_parser.get_exceptions()))

    self.assertTupleEqual(expected_tokens_int, int_parser.get_tokens())
    self.assertTupleEqual(('Unexpected symbol "2" at position 3',), tuple(str(ex) for ex in int_parser.get_exceptions()))

    self.assertTupleEqual(expected_tokens_float1, float1_parser.get_tokens())
    self.assertTupleEqual(('Unexpected symbol "2" at position 4',), tuple(str(ex) for ex in float1_parser.get_exceptions()))

    self.assertTupleEqual(expected_tokens_float2, float2_parser.get_tokens())
    self.assertTupleEqual(('Unexpected symbol "." at position 3',), tuple(str(ex) for ex in float2_parser.get_exceptions()))

    self.assertTupleEqual(expected_tokens_float3, float3_parser.get_tokens())
    self.assertTupleEqual(('Unexpected symbol "2" at position 2',), tuple(str(ex) for ex in float3_parser.get_exceptions()))

    self.assertTupleEqual(expected_tokens_float4, float4_parser.get_tokens())
    self.assertTupleEqual(('Unexpected symbol "." at position 4',), tuple(str(ex) for ex in float4_parser.get_exceptions()))


  def test_invalid_parenthesis_with_constants_order(self):
    lp_parser = ExpressionParser(expression='2( 4')
    wrong_order_parser = ExpressionParser(expression='4) (1')

    expected_lp_tokens = (
      Token.of('2', TokenType.CONSTANT, 0),
      Token.of(Signature.LEFT_PARENTHESIS, TokenType.PARENTHESIS, 1),
      Token.of('4', TokenType.CONSTANT, 3),
    )

    expected_wrong_order_tokens = (
      Token.of('4', TokenType.CONSTANT, 0),
      Token.of(Signature.RIGHT_PARENTHESIS, TokenType.PARENTHESIS, 1),
      Token.of(Signature.LEFT_PARENTHESIS, TokenType.PARENTHESIS, 3),
      Token.of('1', TokenType.CONSTANT, 4),
    )

    self.assertTupleEqual(expected_lp_tokens, lp_parser.get_tokens())
    self.assertTupleEqual((('Unexpected left parenthesis "(" at position 1'),), tuple(str(ex) for ex in lp_parser.get_exceptions()))

    self.assertTupleEqual(expected_wrong_order_tokens, wrong_order_parser.get_tokens())
    self.assertTupleEqual((('Unexpected left parenthesis "(" at position 3'),), tuple(str(ex) for ex in wrong_order_parser.get_exceptions()))


  def test_invalid_parenthesis_with_variables_order(self):
    lp_parser = ExpressionParser(expression='a) b')
    wrong_order_parser = ExpressionParser(expression='a) (b')

    expected_lp_tokens = (
      Token.of('a', TokenType.VARIABLE, 0),
      Token.of(Signature.RIGHT_PARENTHESIS, TokenType.PARENTHESIS, 1),
      Token.of('b', TokenType.VARIABLE, 3),
    )

    expected_wrong_order_tokens = (
      Token.of('a', TokenType.VARIABLE, 0),
      Token.of(Signature.RIGHT_PARENTHESIS, TokenType.PARENTHESIS, 1),
      Token.of(Signature.LEFT_PARENTHESIS, TokenType.PARENTHESIS, 3),
      Token.of('b', TokenType.VARIABLE, 4),
    )

    self.assertTupleEqual(expected_lp_tokens, lp_parser.get_tokens())
    self.assertTupleEqual((('Unexpected symbol "b" at position 3'),), tuple(str(ex) for ex in lp_parser.get_exceptions()))

    self.assertTupleEqual(expected_wrong_order_tokens, wrong_order_parser.get_tokens())
    self.assertTupleEqual((('Unexpected left parenthesis "(" at position 3'),), tuple(str(ex) for ex in wrong_order_parser.get_exceptions()))


  def test_point_in_variable_exception(self):
    parser = ExpressionParser(expression='vari.able')
    expected_tokens = (
      Token(value='vari.able', type=TokenType.VARIABLE, start=0, end=8),
    )
    expected_exceptions = (
      'Unexpected symbol "." at position 4',
    )

    self.assertTupleEqual(expected_tokens, parser.get_tokens())
    self.assertTupleEqual(expected_exceptions, tuple(str(ex) for ex in parser.get_exceptions()))


  def test_delimiter_exceptions(self):
    parser_start = ExpressionParser(expression=',a')
    parser_end = ExpressionParser(expression='a,')
    parser_parenthesis = ExpressionParser(expression='(,)')

    expected_tokens_start = (
      Token.of(Signature.DELIMITER, TokenType.DELIMITER, 0),      
      Token.of('a', TokenType.VARIABLE, 1),
    )
    expected_tokens_end = (
      Token.of('a', TokenType.VARIABLE, 0),
      Token.of(Signature.DELIMITER, TokenType.DELIMITER, 1),      
    )
    expected_tokens_parenthesis = (
      Token.of(Signature.LEFT_PARENTHESIS, TokenType.PARENTHESIS, 0),      
      Token.of(Signature.DELIMITER, TokenType.DELIMITER, 1),
      Token.of(Signature.RIGHT_PARENTHESIS, TokenType.PARENTHESIS, 2),
    )

    self.assertTupleEqual(expected_tokens_start, parser_start.get_tokens())
    self.assertTupleEqual(('Unexpected delimiter symbol "," at position 0',), tuple(str(ex) for ex in parser_start.get_exceptions()))

    self.assertTupleEqual(expected_tokens_end, parser_end.get_tokens())
    self.assertTupleEqual(('Invalid symbol "," at position 1',), tuple(str(ex) for ex in parser_end.get_exceptions()))

    self.assertTupleEqual(expected_tokens_parenthesis, parser_parenthesis.get_tokens())
    self.assertTupleEqual(
      ('Unexpected delimiter symbol "," at position 1', 'Unexpected symbol ")" at position 2'),
      tuple(str(ex) for ex in parser_parenthesis.get_exceptions())
    )


  def test_invalid_operators_parsing(self):
    parser_bu = ExpressionParser(expression='a +/ b')
    parser_bb = ExpressionParser(expression='a ^* b')
    parser_pb = ExpressionParser(expression='( * s')
    parser_bp = ExpressionParser(expression='5 / )')
    parser_up = ExpressionParser(expression='5 - )')

    expected_tokens_bu = (
      Token.of('a', TokenType.VARIABLE, 0),
      Token.of(Operator.PLUS.value, TokenType.OPERATOR, 2),
      Token.of(Operator.DIVIDE.value, TokenType.OPERATOR, 3),
      Token.of('b', TokenType.VARIABLE, 5),
    )
    expected_tokens_bb = (
      Token.of('a', TokenType.VARIABLE, 0),
      Token.of(Operator.POWER.value, TokenType.OPERATOR, 2),
      Token.of(Operator.MULTIPLY.value, TokenType.OPERATOR, 3),
      Token.of('b', TokenType.VARIABLE, 5),
    )
    expected_tokens_pb = (
      Token.of(Signature.LEFT_PARENTHESIS, TokenType.PARENTHESIS, 0),
      Token.of(Operator.MULTIPLY.value, TokenType.OPERATOR, 2),
      Token.of('s', TokenType.VARIABLE, 4),
    )
    expected_tokens_bp = (
      Token.of('5', TokenType.CONSTANT, 0),
      Token.of(Operator.DIVIDE.value, TokenType.OPERATOR, 2),
      Token.of(Signature.RIGHT_PARENTHESIS, TokenType.PARENTHESIS, 4),
    )
    expected_tokens_up = (
      Token.of('5', TokenType.CONSTANT, 0),
      Token.of(Operator.MINUS.value, TokenType.OPERATOR, 2),
      Token.of(Signature.RIGHT_PARENTHESIS, TokenType.PARENTHESIS, 4),
    )

    self.assertTupleEqual(expected_tokens_bu, parser_bu.get_tokens())
    self.assertTupleEqual(('Invalid symbol operator "/" at position 3',), tuple(str(ex) for ex in parser_bu.get_exceptions()))

    self.assertTupleEqual(expected_tokens_bb, parser_bb.get_tokens())
    self.assertTupleEqual(('Invalid symbol operator "*" at position 3',), tuple(str(ex) for ex in parser_bb.get_exceptions()))

    self.assertTupleEqual(expected_tokens_pb, parser_pb.get_tokens())
    self.assertTupleEqual(('Invalid symbol operator "*" at position 2',), tuple(str(ex) for ex in parser_pb.get_exceptions()))

    self.assertTupleEqual(expected_tokens_bp, parser_bp.get_tokens())
    self.assertTupleEqual(('Unexpected symbol ")" at position 4',), tuple(str(ex) for ex in parser_bp.get_exceptions()))

    self.assertTupleEqual(expected_tokens_up, parser_up.get_tokens())
    self.assertTupleEqual(('Unexpected symbol ")" at position 4',), tuple(str(ex) for ex in parser_up.get_exceptions()))

  def test_invalid_delimiter_order(self):
    parser_pd = ExpressionParser(expression='(,5')
    parser_dp = ExpressionParser(expression='5,)')
    parser_od = ExpressionParser(expression='+,5')
    parser_do = ExpressionParser(expression='5,*')
    parser_dd = ExpressionParser(expression='a,,5')

    expected_tokens_pd = (
      Token.of(Signature.LEFT_PARENTHESIS, TokenType.PARENTHESIS, 0),
      Token.of(Signature.DELIMITER, TokenType.DELIMITER, 1),
      Token.of('5', TokenType.CONSTANT, 2),
    )
    expected_tokens_dp = (
      Token.of('5', TokenType.CONSTANT, 0),
      Token.of(Signature.DELIMITER, TokenType.DELIMITER, 1),
      Token.of(Signature.RIGHT_PARENTHESIS, TokenType.PARENTHESIS, 2),
    )
    expected_tokens_od = (
      Token.of(Operator.PLUS.value, TokenType.OPERATOR, 0),
      Token.of(Signature.DELIMITER, TokenType.DELIMITER, 1),
      Token.of('5', TokenType.CONSTANT, 2),
    )
    expected_tokens_do = (
      Token.of('5', TokenType.CONSTANT, 0),
      Token.of(Signature.DELIMITER, TokenType.DELIMITER, 1),
      Token.of(Operator.MULTIPLY.value, TokenType.OPERATOR, 2),
    )
    expected_tokens_dd = (
      Token.of('a', TokenType.VARIABLE, 0),
      Token.of(Signature.DELIMITER, TokenType.DELIMITER, 1),
      Token.of(Signature.DELIMITER, TokenType.DELIMITER, 2),
      Token.of('5', TokenType.CONSTANT, 3),
    )

    self.assertTupleEqual(expected_tokens_pd, parser_pd.get_tokens())
    self.assertTupleEqual(('Unexpected delimiter symbol "," at position 1',), tuple(str(ex) for ex in parser_pd.get_exceptions()))

    self.assertTupleEqual(expected_tokens_dp, parser_dp.get_tokens())
    self.assertTupleEqual(('Unexpected symbol ")" at position 2',), tuple(str(ex) for ex in parser_dp.get_exceptions()))

    self.assertTupleEqual(expected_tokens_od, parser_od.get_tokens())
    self.assertTupleEqual(('Unexpected delimiter symbol "," at position 1',), tuple(str(ex) for ex in parser_od.get_exceptions()))

    self.assertTupleEqual(expected_tokens_do, parser_do.get_tokens())
    self.assertTupleEqual(('Invalid symbol "*" at position 2',), tuple(str(ex) for ex in parser_do.get_exceptions()))

    self.assertTupleEqual(expected_tokens_dd, parser_dd.get_tokens())
    self.assertTupleEqual(('Unexpected delimiter symbol "," at position 2',), tuple(str(ex) for ex in parser_dd.get_exceptions()))


  def test_unary_operators_parsing(self):
    parser_u = ExpressionParser(expression='-+(-a)')
    parser_bu = ExpressionParser(expression='a--+b')
    parser_ue = ExpressionParser(expression='-(+1^-8)')
    parser_ue2 = ExpressionParser(expression='+sin(-4)/-(5)')

    expected_tokens_u = (
      Token.of(Operator.MINUS.value, TokenType.OPERATOR, 0),
      Token.of(Operator.PLUS.value, TokenType.OPERATOR, 1),
      Token.of(Signature.LEFT_PARENTHESIS, TokenType.PARENTHESIS, 2),
      Token.of(Operator.MINUS.value, TokenType.OPERATOR, 3),
      Token.of('a', TokenType.VARIABLE, 4),
      Token.of(Signature.RIGHT_PARENTHESIS, TokenType.PARENTHESIS, 5),
    )
    expected_tokens_bu = (
      Token.of('a', TokenType.VARIABLE, 0),
      Token.of(Operator.MINUS.value, TokenType.OPERATOR, 1),
      Token.of(Operator.MINUS.value, TokenType.OPERATOR, 2),
      Token.of(Operator.PLUS.value, TokenType.OPERATOR, 3),
      Token.of('b', TokenType.VARIABLE, 4),
    )
    expected_tokens_ue = (
      Token.of(Operator.MINUS.value, TokenType.OPERATOR, 0),
      Token.of(Signature.LEFT_PARENTHESIS, TokenType.PARENTHESIS, 1),
      Token.of(Operator.PLUS.value, TokenType.OPERATOR, 2),
      Token.of('1', TokenType.CONSTANT, 3),
      Token.of(Operator.POWER.value, TokenType.OPERATOR, 4),
      Token.of(Operator.MINUS.value, TokenType.OPERATOR, 5),
      Token.of('8', TokenType.CONSTANT, 6),
      Token.of(Signature.RIGHT_PARENTHESIS, TokenType.PARENTHESIS, 7),
    )
    expected_tokens_ue2 = (
      Token.of(Operator.PLUS.value, TokenType.OPERATOR, 0),
      Token(value='sin', type=TokenType.FUNCTION, start=1, end=3),
      Token.of(Signature.LEFT_PARENTHESIS, TokenType.PARENTHESIS, 4),
      Token.of(Operator.MINUS.value, TokenType.OPERATOR, 5),
      Token.of('4', TokenType.CONSTANT, 6),
      Token.of(Signature.RIGHT_PARENTHESIS, TokenType.PARENTHESIS, 7),
      Token.of(Operator.DIVIDE.value, TokenType.OPERATOR, 8),
      Token.of(Operator.MINUS.value, TokenType.OPERATOR, 9),
      Token.of(Signature.LEFT_PARENTHESIS, TokenType.PARENTHESIS, 10),
      Token.of('5', TokenType.CONSTANT, 11),
      Token.of(Signature.RIGHT_PARENTHESIS, TokenType.PARENTHESIS, 12),
    )

    self.assertTupleEqual(expected_tokens_u, parser_u.get_tokens())
    self.assertTupleEqual(tuple(), parser_u.get_exceptions())

    self.assertTupleEqual(expected_tokens_bu, parser_bu.get_tokens())
    self.assertTupleEqual(tuple(), parser_bu.get_exceptions())

    self.assertTupleEqual(expected_tokens_ue, parser_ue.get_tokens())
    self.assertTupleEqual(tuple(), parser_ue.get_exceptions())

    self.assertTupleEqual(expected_tokens_ue2, parser_ue2.get_tokens())
    self.assertTupleEqual(tuple(), parser_ue2.get_exceptions())

  
  def test_multiple_exceptions_expression(self):
    parser = ExpressionParser( 's . 2 + ) d /')
    expected_tokens = (
      Token(value='s . 2', type=TokenType.VARIABLE, start=0, end=4),
      Token.of(Operator.PLUS.value, TokenType.OPERATOR, 6),
      Token.of(Signature.RIGHT_PARENTHESIS, TokenType.PARENTHESIS, 8),
      Token.of('d', TokenType.VARIABLE, 10),
      Token.of(Operator.DIVIDE.value, TokenType.OPERATOR, 12),
    )
    expected_exceptions = (
      'Unexpected symbol "." at position 2',
      'Unexpected symbol "2" at position 4',
      'Unexpected symbol ")" at position 8',
      'Unexpected symbol "d" at position 10',
      'Unexpected symbol "/" at position 12',
    )

    self.assertTupleEqual(expected_tokens, parser.get_tokens())
    self.assertTupleEqual(expected_exceptions, tuple(str(ex) for ex in parser.get_exceptions()))
