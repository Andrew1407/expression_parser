from parser.expression_parser import ExpressionParser, ParsingExeprion
from analyzer.syntax_analyzer import SyntaxAnalyzer, SyntaxAnalysisException
from parallel_tree.builder import build_parallel_tree
from tree_output.expression_view import ExpressionView


class ConsoleInputClient:
  def __init__(self, output: ExpressionView):
    self.__output = output
  

  def pass_input(self, expression: str):
    if expression:
      self.__exceptions_wrapper(expression)


  def __parse_expression(self, expression: str):
    ep = ExpressionParser(expression)
    tokens = ep.get_tokens()
    self.__output.show_tokens(tokens)
    parsing_exceptions = ep.get_exceptions()
    if parsing_exceptions:
      raise ExceptionGroup('Parsing errors', parsing_exceptions)
    sa = SyntaxAnalyzer(tokens)
    syntax_tree = sa.get_tree()
    self.__output.show_syntax_tree(syntax_tree)
    parallel_tree = build_parallel_tree(syntax_tree)
    self.__output.show_parallel_tree(parallel_tree)


  def __exceptions_wrapper(self, expression: str):
    try:
      self.__parse_expression(expression)
    except ExceptionGroup as eg:
      exceptions = eg.exceptions
      is_parsing_exceptions = all(isinstance(e, ParsingExeprion) for e in exceptions)
      if not is_parsing_exceptions: raise
      self.__output.show_parsing_exceptions(eg.message, exceptions)
    except SyntaxAnalysisException as e:
      self.__output.show_syntax_exception(e)



if __name__ == '__main__':
  expression_view = ExpressionView()
  input_client = ConsoleInputClient(expression_view)
  while True:
    try:
      expression = input('> ')
      input_client.pass_input(expression)
    except (KeyboardInterrupt, EOFError):
      print()
      break
