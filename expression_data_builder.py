from typing import Callable
from expression_parser.parser.expression_parser import ExpressionParser, ParsingExeprion, Token
from expression_parser.analyzer.syntax_analyzer import SyntaxAnalyzer, SyntaxAnalysisException, Node
from expression_parser.parallel_tree.builder import build_parallel_tree
from expression_parser.parallel_tree.optimizer_tools import open_brackets
from expression_parser.tree_output.expression_view import ExpressionView
from expression_parser.equivalent_forms.distributivity import apply_distribution
from expression_parser.equivalent_forms.commutativity import apply_commutation
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
  

  def build_equivalent_forms(self, tree: Node) -> tuple[Node, Node]:
    distributive_form = build_parallel_tree(apply_distribution(tree))
    commutative_form = build_parallel_tree(apply_commutation(tree))
    self.__output.show_distributivity_expression(distributive_form)
    self.__output.show_commutativity_expression(commutative_form)
    return open_brackets(distributive_form), open_brackets(commutative_form)

  
  def build_conveyor_simulations(self, default: Node, distributive: Node, commutative: Node):
    nodes = dict(
      default=(default, self.__output.log_dafault_conveyor_data),
      distributive=(distributive, self.__output.log_distributive_conveyor_data),
      commutative=(commutative, self.__output.log_commutative_form_conveyor_data),
    )
    results = dict()
    for key, container in nodes.items():
      expression, logger = container
      dc = DynamicConveyor.of(expression)
      simulation_results = dc.simulate()
      logger(simulation_results)
      results[key] = simulation_results
    self.__output.log_efficiency_table(results)
