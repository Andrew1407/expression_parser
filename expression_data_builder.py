from typing import Callable
from expression_parser.parser.expression_parser import ExpressionParser, ParsingExeprion, Token
from expression_parser.analyzer.syntax_analyzer import SyntaxAnalyzer, SyntaxAnalysisException, Node
from expression_parser.parallel_tree.builder import build_parallel_tree
from expression_parser.parallel_tree.optimizer_tools import open_brackets
from expression_parser.tree_output.expression_view import ExpressionView
from expression_parser.equivalent_forms.distributivity import generate_distributivity_forms
from expression_parser.equivalent_forms.commutativity import generate_commutativity_forms
from expression_parser.conveyor_simulation.dynamic import DynamicConveyor


class ExpressionDataBuilder:
  def __init__(self, output: ExpressionView):
    self.__output = output


  def exceptions_wrapper(self, parser: Callable, *args):
    try:
      parser(*args)
    except ExceptionGroup as eg:
      exceptions = eg.exceptions
      is_parsing_exceptions = all(isinstance(e, ParsingExeprion) for e in exceptions)
      if not is_parsing_exceptions: raise
      self.__output.show_parsing_exceptions(eg.message, exceptions)
    except SyntaxAnalysisException as e:
      self.__output.show_syntax_exception(e)
  

  def build_token_list(self, expression: str) -> tuple[Token]:
    ep = ExpressionParser(expression)
    tokens = ep.get_tokens()
    self.__output.show_tokens(tokens)
    parsing_exceptions = ep.get_exceptions()
    if parsing_exceptions:
      raise ExceptionGroup('Parsing errors', parsing_exceptions)
    return tokens


  def build_syntax_tree(self, tokens: tuple[Token]) -> Node:
    sa = SyntaxAnalyzer(tokens)
    syntax_tree = sa.get_tree()
    self.__output.show_syntax_tree(syntax_tree)
    parallel_tree = build_parallel_tree(syntax_tree)
    self.__output.show_parallel_tree(parallel_tree)
    return open_brackets(parallel_tree)
  

  def build_equivalent_forms(self, tree: Node) -> tuple[tuple[Node], tuple[Node]]:
    list_limit = 5
    distributivity_forms = tuple(map(build_parallel_tree, generate_distributivity_forms(tree)))
    commutativity_forms = tuple(map(build_parallel_tree, generate_commutativity_forms(tree)))
    self.__output.log_distributivity_forms(distributivity_forms, list_limit)
    self.__output.log_commutativity_forms(commutativity_forms, list_limit)
    open_brackets_tuple = lambda forms: tuple(open_brackets(n) for n in forms)
    return open_brackets_tuple(distributivity_forms), open_brackets_tuple(commutativity_forms)


  def build_conveyor_simulations(self, default: Node, distributive: tuple[Node], commutative: tuple[Node]):
    generate_results = lambda n: (n, DynamicConveyor.of(n).simulate())
    default_results = generate_results(default)
    self.__output.log_dafault_conveyor_data(default_results[1])
    factor = 'efficiency'
    distributive_results = tuple(map(generate_results, distributive))
    commutative_results = tuple(map(generate_results, commutative))
    log_node =  lambda data: max(data, key=lambda n: getattr(n[1], factor))
    self.__output.log_distributive_conveyor_data(*log_node(distributive_results))
    self.__output.log_distributive_conveyor_data(*log_node(commutative_results))
    self.__output.log_efficiency_table((default_results, *distributive_results, *commutative_results), factor)
