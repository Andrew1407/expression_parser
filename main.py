from parser.expression_parser import ExpressionParser
from analyzer.syntax_analyzer import SyntaxAnalyzer


def parse_expression(expression):
  ep = ExpressionParser(expression)
  parsing_exceptions = ep.get_exceptions()
  print('Parsed tokens:')
  tokens = ep.get_tokens()
  for t in tokens: print(t)
  if parsing_exceptions:
    print('\nParsing errors:')
    for e in ep.get_exceptions(): print(e)
    return
  sa = SyntaxAnalyzer(tokens)
  print('\nSyntax tree:')
  print(sa.get_tree())


if __name__ =='__main__':
  expression = '33, 9'
  parse_expression(expression)
