from parser.expression_parser import ExpressionParser
from analyzer.syntax_analyzer import SyntaxAnalyzer, SyntaxAnalysisException


def parse_expression(expression):
  ep = ExpressionParser(expression)
  parsing_exceptions = ep.get_exceptions()
  print('Parsed tokens:')
  tokens = ep.get_tokens()
  if tokens:
    for t in tokens: print(t.to_json())
  else:
    print('Empty array')
  if parsing_exceptions:
    print('\nParsing errors:')
    for e in ep.get_exceptions(): print(e)
    return
  try:
    sa = SyntaxAnalyzer(tokens)
    print('\nSyntax tree:')
    print(sa.get_tree().to_json())
  except SyntaxAnalysisException as ex:
    print('\nSyntax errors:')
    print(ex)


if __name__ =='__main__':
  while True:
    try:
      expression = input('> ')
      if expression: parse_expression(expression)
    except BaseException as ex:
      match ex:
        case KeyboardInterrupt() | EOFError():
          print()
          break
        case _:
          raise ex
