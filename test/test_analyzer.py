import unittest
from expression_parser.parser.tokens import Token, TokenType, Signature, Operator
from expression_parser.parser.expression_parser import ExpressionParser
from expression_parser.analyzer.syntax_analyzer import SyntaxAnalyzer, SyntaxAnalysisException
from expression_parser.analyzer.tree_nodes import Node, BinaryOperatorNode, UnaryOperatorNode, FunctionNode


class TestExpressionParser(unittest.TestCase):
  def __build_tree(self, expression: str) -> Node:
    ep = ExpressionParser(expression)
    sa = SyntaxAnalyzer(ep.get_tokens())
    return sa.get_tree()


  def test_empty_tokens_list_case(self):
    result = self.__build_tree(expression=str())
    expected = Node(value=None)

    self.assertEqual(expected, result)

  
  def test_operators_nesting(self):
    result = self.__build_tree(expression='-(p + 3) + (-4 ^ 2)')
    expected = BinaryOperatorNode(
      value=Token.of(Operator.PLUS.value, TokenType.OPERATOR, 9),
      left=UnaryOperatorNode(
        value=Token.of(Operator.MINUS.value, TokenType.OPERATOR, 0),
        expression=BinaryOperatorNode(
          value=Token.of(Operator.PLUS.value, TokenType.OPERATOR, 4),
          left=Node(value=Token.of('p', TokenType.VARIABLE, 2)),
          right=Node(value=Token.of('3', TokenType.CONSTANT, 6)),
        ),
      ),
      right=BinaryOperatorNode(
        value=Token.of(Operator.POWER.value, TokenType.OPERATOR, 15),
        left=UnaryOperatorNode(
          value=Token.of(Operator.MINUS.value, TokenType.OPERATOR, 12),
          expression=Node(value=Token.of('4', TokenType.CONSTANT, 13))
        ),
        right=Node(Token.of('2', TokenType.CONSTANT, 17)),
      ),
    )

    self.assertEqual(expected, result)


  def test_operator_priorities(self):
    result1 = self.__build_tree(expression='a +  b * c')
    result2 = self.__build_tree(expression='a + (b * c)')
    expected = BinaryOperatorNode(
      value=Token.of(Operator.PLUS.value, TokenType.OPERATOR, 2),
      left=Node(value=Token.of('a', TokenType.VARIABLE, 0)),
      right=BinaryOperatorNode(
        value=Token.of(Operator.MULTIPLY.value, TokenType.OPERATOR, 7),
        left=Node(value=Token.of('b', TokenType.VARIABLE, 5)),
        right=Node(value=Token.of('c', TokenType.VARIABLE, 9)),
      ),
    )

    self.assertEqual(expected, result1)
    self.assertEqual(expected, result2)

  
  def test_parentheses_priority(self):
    result = self.__build_tree(expression='(a + b) * c')
    expected = BinaryOperatorNode(
      value=Token.of(Operator.MULTIPLY.value, TokenType.OPERATOR, 8),
      left=BinaryOperatorNode(
        value=Token.of(Operator.PLUS.value, TokenType.OPERATOR, 3),
        left=Node(value=Token.of('a', TokenType.VARIABLE, 1)),
        right=Node(value=Token.of('b', TokenType.VARIABLE, 5)),
      ),
      right=Node(value=Token.of('c', TokenType.VARIABLE, 10)),
    )

    self.assertEqual(expected, result)


  def test_function_node(self):
    no_args = self.__build_tree(expression='rand()')
    one_args = self.__build_tree(expression='sin(cos(4))')
    two_args = self.__build_tree(expression='max(3 * k, 4)')

    no_args_expected = FunctionNode(
      value=Token(value='rand', type=TokenType.FUNCTION, start=0, end=3),
      args=tuple(),
    )
    one_args_expected = FunctionNode(
      value=Token(value='sin', type=TokenType.FUNCTION, start=0, end=2),
      args=(
        FunctionNode(
          value=Token(value='cos', type=TokenType.FUNCTION, start=4, end=6),
          args=(
            Node(value=Token.of('4', TokenType.CONSTANT, 8)),
          ),
        ),
      ),
    )
    two_args_expected = FunctionNode(
      value=Token(value='max', type=TokenType.FUNCTION, start=0, end=2),
      args=(
        BinaryOperatorNode(
          value=Token.of(Operator.MULTIPLY.value, TokenType.OPERATOR, 6),
          left=Node(value=Token.of('3', TokenType.CONSTANT, 4)),
          right=Node(value=Token.of('k', TokenType.VARIABLE, 8)),
        ),
        Node(value=Token.of('4', TokenType.CONSTANT, 11)),
      ),
    )

    self.assertEqual(no_args, no_args_expected)
    self.assertEqual(one_args, one_args_expected)
    self.assertEqual(two_args, two_args_expected)


  def test_function_call_exception(self):
    token_before = Token(value='sin', type=TokenType.FUNCTION, start=4, end=6)
    token_after = Token(value='sin', type=TokenType.FUNCTION, start=0, end=2)
    expected = 'Declared function "sin()" sould be called: "{}"'

    with self.assertRaises(SyntaxAnalysisException) as context_before:
      self.__build_tree(expression='4 + sin')

    with self.assertRaises(SyntaxAnalysisException) as context_after:
      self.__build_tree(expression='sin + 4')

    self.assertEqual(expected.format(token_before), str(context_before.exception))
    self.assertEqual(expected.format(token_after), str(context_after.exception))

  
  def test_undefined_function_call(self):
    token = Token(value='fn', type=TokenType.VARIABLE, start=0, end=1)
    expected = 'No such function, cannot call: "{}"'

    with self.assertRaises(SyntaxAnalysisException) as context_no_args:
      self.__build_tree(expression='fn()')

    with self.assertRaises(SyntaxAnalysisException) as context_one_arg:
      self.__build_tree(expression='fn(3)')

    with self.assertRaises(SyntaxAnalysisException) as context_many_args:
      self.__build_tree(expression='fn(3, d45, d)')

    self.assertEqual(expected.format(token), str(context_no_args.exception))
    self.assertEqual(expected.format(token), str(context_one_arg.exception))
    self.assertEqual(expected.format(token), str(context_many_args.exception))


  def test_too_few_args_exception(self):
    expected = 'Too few arguments (given: {}) for called funtion (expected: {}): "{}"'
    token1 = Token(value='sin', type=TokenType.FUNCTION, start=0, end=2)
    token2 = Token(value='max', type=TokenType.FUNCTION, start=0, end=2)

    with self.assertRaises(SyntaxAnalysisException) as context_no_args:
      self.__build_tree(expression='sin()')

    with self.assertRaises(SyntaxAnalysisException) as context_one_arg:
      self.__build_tree(expression='max(3)')

    self.assertEqual(expected.format(0, 1, token1), str(context_no_args.exception))
    self.assertEqual(expected.format(1, 2, token2), str(context_one_arg.exception))


  def test_too_many_args_exception(self):
    expected = 'Too many arguments (given: {}) for called funtion (expected: {}): "{}"'
    token1 = Token(value='rand', type=TokenType.FUNCTION, start=0, end=3)
    token2 = Token(value='sin', type=TokenType.FUNCTION, start=0, end=2)
    token3 = Token(value='max', type=TokenType.FUNCTION, start=0, end=2)

    with self.assertRaises(SyntaxAnalysisException) as context_no_args:
      self.__build_tree(expression='rand(23)')

    with self.assertRaises(SyntaxAnalysisException) as context_one_arg:
      self.__build_tree(expression='sin(kg, 3)')

    with self.assertRaises(SyntaxAnalysisException) as context_two_args:
      self.__build_tree(expression='max(kg, 3, aj_io9)')

    self.assertEqual(expected.format(1, 0, token1), str(context_no_args.exception))
    self.assertEqual(expected.format(2, 1, token2), str(context_one_arg.exception))
    self.assertEqual(expected.format(3, 2, token3), str(context_two_args.exception))

  
  def test_redundant_parenthesis_exception(self):
    token1 = Token.of(Signature.LEFT_PARENTHESIS, TokenType.PARENTHESIS, 4)
    token2 = Token.of(Signature.RIGHT_PARENTHESIS, TokenType.PARENTHESIS, 6)
    expected1 = 'No right parenthesis found for: "{}"; expecting ")"'
    expected2 = 'Unexpected token: "{}"'

    with self.assertRaises(SyntaxAnalysisException) as context_lp:
      self.__build_tree(expression='2 + ((7+s) + 4')

    with self.assertRaises(SyntaxAnalysisException) as context_rp:
      self.__build_tree(expression='2 +(7)) + 4')

    with self.assertRaises(SyntaxAnalysisException) as context_rp_fn:
      self.__build_tree(expression='rand()) + 9')

    self.assertEqual(expected1.format(token1), str(context_lp.exception))
    self.assertEqual(expected2.format(token2), str(context_rp.exception))
    self.assertEqual(expected2.format(token2), str(context_rp_fn.exception))


  def test_missing_parenthesis_exception(self):
    token1 = Token(value='sin', type=TokenType.FUNCTION, start=0, end=2)
    token2 = Token.of(Signature.LEFT_PARENTHESIS, TokenType.PARENTHESIS, 4)
    token3 = Token.of(Signature.RIGHT_PARENTHESIS, TokenType.PARENTHESIS, 5)
    expected1 = 'Right parenthesis expected for: "{}"'
    expected2 = 'No right parenthesis found for: "{}"; expecting ")"'
    expected3 = 'Unexpected token: "{}"'

    with self.assertRaises(SyntaxAnalysisException) as context_fn:
      self.__build_tree(expression='sin( 9')

    with self.assertRaises(SyntaxAnalysisException) as context_rp:
      self.__build_tree(expression='d + (f - 8')

    with self.assertRaises(SyntaxAnalysisException) as context_lp:
      self.__build_tree(expression='w + r) - 8')

    self.assertEqual(expected1.format(token1), str(context_fn.exception))
    self.assertEqual(expected2.format(token2), str(context_rp.exception))
    self.assertEqual(expected3.format(token3), str(context_lp.exception))
