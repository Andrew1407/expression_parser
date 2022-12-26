from expression_parser.parser.expression_parser import ExpressionParser, ParsingExeprion, Token
from expression_parser.analyzer.syntax_analyzer import SyntaxAnalyzer, SyntaxAnalysisException, Node
from expression_parser.parallel_tree.builder import build_parallel_tree
from expression_parser.parallel_tree.optimizer_tools import open_brackets
from expression_parser.tree_output.expression_view import ExpressionView
from expression_parser.equivalent_forms.distributivity import apply_distribution
from expression_parser.equivalent_forms.commutativity import apply_commutation
from expression_parser.conveyor_simulation.dynamic import DynamicConveyor

from expression_parser.tree_output.str_converter import stringify_tree


class ConsoleInputClient:
  def __init__(self, output: ExpressionView):
    self.__output = output
  

  def pass_input(self, expression: str):
    if expression:
      self.__exceptions_wrapper(expression)


  def __parse_expression(self, expression: str):
    tokens = self.__build_token_list(expression)
    parallel_tree = self.__build_syntax_tree(tokens)
    distributive_form, commutative_form = self.__build_equivalent_forms(parallel_tree)

    layers = 4
    dc = DynamicConveyor(parallel_tree, layers=layers)
    simulation_results = dc.simulate()
    print(f'{simulation_results.sequential=} {simulation_results.dynamic=}')
    for s in simulation_results.steps:
      print(f'{s.tacts=}')
      print([ stringify_tree(sn) if sn else sn for sn in s.layers ])


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

  
  def __build_token_list(self, expression: str) -> tuple[Token]:
    ep = ExpressionParser(expression)
    tokens = ep.get_tokens()
    self.__output.show_tokens(tokens)
    parsing_exceptions = ep.get_exceptions()
    if parsing_exceptions:
      raise ExceptionGroup('Parsing errors', parsing_exceptions)
    return tokens
  

  def __build_syntax_tree(self, tokens: tuple[Token]) -> Node:
    sa = SyntaxAnalyzer(tokens)
    syntax_tree = sa.get_tree()
    self.__output.show_syntax_tree(syntax_tree)
    parallel_tree = build_parallel_tree(syntax_tree)
    self.__output.show_parallel_tree(parallel_tree)
    return open_brackets(parallel_tree)
  

  def __build_equivalent_forms(self, tree: Node) -> tuple[Node, Node]:
    distributive_form = build_parallel_tree(apply_distribution(tree))
    commutative_form = build_parallel_tree(apply_commutation(tree))
    self.__output.show_distributivity_expression(distributive_form)
    self.__output.show_commutativity_expression(commutative_form)
    return open_brackets(distributive_form), open_brackets(commutative_form)


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
