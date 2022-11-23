from parser.expression_parser import ExpressionParser, ParsingExeprion
from analyzer.syntax_analyzer import SyntaxAnalyzer, SyntaxAnalysisException
from parallel_tree.builder import build_parallel_tree


def exception_handler(fn):
  def wrapper(*args, **kwargs):
    try:
      fn(*args, **kwargs)
    except ExceptionGroup as eg:
      exceptions = eg.exceptions
      is_parsing_exceptions = all(isinstance(e, ParsingExeprion) for e in exceptions)
      if not is_parsing_exceptions: raise
      print(f'\n{eg.message}:')
      for e in exceptions: print(e)
    except SyntaxAnalysisException as e:
      print('\nSyntax error:\n', e)

  return wrapper


@exception_handler
def parse_expression(expression):
  ep = ExpressionParser(expression)
  print('Parsed tokens:')
  tokens = ep.get_tokens()
  if tokens:
    for t in tokens: print(t.to_json())
  else:
    print('Empty array')
  parsing_exceptions = ep.get_exceptions()
  if parsing_exceptions:
    raise ExceptionGroup('Parsing errors', parsing_exceptions)
  sa = SyntaxAnalyzer(tokens)
  syntax_tree = sa.get_tree()
  print('\nSyntax tree:\n', syntax_tree.to_json())
  parallel_tree = build_parallel_tree(syntax_tree)
  print('\nParallel tree:\n', parallel_tree.to_json())


if __name__ == '__main__':
  while True:
    try:
      expression = input('> ')
      if expression: parse_expression(expression)
    except (KeyboardInterrupt, EOFError):
      print()
      break
