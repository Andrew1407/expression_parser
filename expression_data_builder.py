from typing import Callable
from expression_parser.parser.expression_parser import ExpressionParser, ParsingExeprion, Token
from expression_parser.analyzer.syntax_analyzer import SyntaxAnalyzer, SyntaxAnalysisException, Node, NodesTuple
from expression_parser.parallel_tree.builder import build_parallel_tree
from expression_parser.parallel_tree.optimizer_tools import open_brackets
from expression_parser.tree_output.expression_view import ExpressionView
from expression_parser.tree_output.str_converter import stringify_tree
from expression_parser.equivalent_forms.distributivity import generate_distributivity_forms
from expression_parser.equivalent_forms.commutativity import generate_commutativity_forms
from expression_parser.conveyor_simulation.dynamic import DynamicConveyor, SimulationData


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
  

  def build_token_list(self, expression: str) -> tuple[Token, ...]:
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
  

  def build_equivalent_forms(self, tree: Node) -> tuple[NodesTuple, NodesTuple]:
    list_limit = 5
    distributivity_forms = self.__get_filtered_equivalent_form(tree, generate_distributivity_forms)
    commutativity_forms = self.__get_filtered_equivalent_form(tree, generate_commutativity_forms)
    self.__output.log_distributivity_forms(distributivity_forms, list_limit)
    self.__output.log_commutativity_forms(commutativity_forms, list_limit)
    open_brackets_tuple = lambda forms: tuple(open_brackets(n) for n in forms)
    return open_brackets_tuple(distributivity_forms), open_brackets_tuple(commutativity_forms)


  def build_conveyor_simulations(self, default: Node, distributive: NodesTuple, commutative: NodesTuple):
    default_results = self.__apply_simulation((default,), '')
    self.__output.log_dafault_conveyor_data(default_results[0][1])
    factor = 'efficiency'
    default_str = stringify_tree(default)
    distributive_results = self.__apply_simulation(distributive, default_str)
    commutative_results = self.__apply_simulation(commutative, default_str)
    log_node =  lambda data: min(data, key=lambda n: getattr(n[1], factor))
    if distributive_results:
      self.__output.log_distributive_conveyor_data(*log_node(distributive_results))
    if commutative_results:
      self.__output.log_commutative_form_conveyor_data(*log_node(commutative_results))
    self.__output.log_efficiency_table(default_results + distributive_results + commutative_results, factor)


  def __apply_simulation(self, expressions: NodesTuple, deafult: str) -> tuple[tuple[Node, SimulationData], ...]:
    forms = ((n, DynamicConveyor.of(n).simulate()) for n in expressions)
    return tuple(f for f in forms if stringify_tree(f[0]) != deafult)


  def __get_filtered_equivalent_form(self, tree: Node, generator: Callable[[Node], NodesTuple]) -> NodesTuple:
    default = stringify_tree(tree)
    forms = ((stringify_tree(n), n) for n in map(build_parallel_tree, generator(tree)))
    unique = {k: v for k, v in forms if k != default}
    return tuple(unique.values())
