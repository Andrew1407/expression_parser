from typing import Sequence
from expression_parser.parser.expression_parser import ParsingExeprion
from expression_parser.parser.tokens import Token
from expression_parser.analyzer.syntax_analyzer import SyntaxAnalysisException
from expression_parser.analyzer.tree_nodes import Node, BinaryOperatorNode, FunctionNode
from expression_parser.conveyor_simulation.containers import SimulationData
from .str_converter import stringify_tree


ROUND_PARAM_DIGITS = 4


def log_tokens(tokens: Sequence[Token]):
  print('Parsed tokens:')
  if tokens:
    for t in tokens: print(t.to_json())
  else:
    print('Empty array')


def log_parsing_exception(message: str, exceptions: ParsingExeprion):
  print(f'\n{message}:')
  for e in exceptions: print(e)


def log_syntax_exception(exception: SyntaxAnalysisException):
  print('\nSyntax error:\n', exception)


def log_syntax_tree(tree: Node):
  print('\nSyntax tree:\n', tree.to_json())


def log_parallel_tree(tree: Node):
  print('\nParallel tree:\n', tree.to_json())


def log_commutativity_forms(expressions: Sequence[Node], take: int = 0):
  print('\nCommutative forms:')
  show_expressions_list(expressions, take)


def log_distributivity_forms(expressions: Sequence[Node], take: int = 0):
  print('\nDistributive forms:')
  show_expressions_list(expressions, take)


def log_efficiency_table(expressions: Sequence[tuple[Node, SimulationData]], factor: str = 'efficiency'):
  ordered = sorted(expressions, key=lambda t: getattr(t[1], factor))
  print('\nEfficiency table for expression forms:')
  logged = list()
  i = 1
  for key, expr in ordered:
    stringified = stringify_tree(key)
    if stringified in logged: continue
    print('%d) %s: %s' % (i, stringified, expr.format_params(round_digits=ROUND_PARAM_DIGITS)))
    i += 1
    logged.append(stringified)


def log_default_conveyor_data(data: SimulationData):
  print('\nConveyor simulation for default expression:\n')
  log_conveyor_data(data)


def log_commutative_form_conveyor_data(tree: Node, data: SimulationData):
  print('\nConveyor simulation for commutative form:')
  print(stringify_tree(tree), '\n')
  log_conveyor_data(data)


def log_distributive_conveyor_data(tree: Node, data: SimulationData):
  print('\nConveyor simulation for distributive form:')
  print(stringify_tree(tree), '\n')
  log_conveyor_data(data)


def show_expressions_list(expressions: Sequence[Node], take: int):
  shorten = take < len(expressions)
  if shorten:
    expressions = expressions[:take]
  for tree in expressions:
    print(stringify_tree(tree))
  if shorten: print('...')


def log_conveyor_data(data: SimulationData):
  formulas: dict[str, Node] = dict()
  node_number = 1
  for i, step in enumerate(data.steps):
    print(f'Step {i+1} - {step.tacts} tact(s):')
    entries: list[str] = list()
    for e in step.layers:
      if e is None:
        entries.append('...')
        continue
      label = __find_formula(formulas, e)
      if label:
        entries.append(label)
        continue
      label = '0_%d' % node_number
      node_number += 1
      formula = str()
      match e:
        case BinaryOperatorNode():
          left_label = __find_formula(formulas, e.left)
          left = left_label if left_label else stringify_tree(e.left)
          right_label = __find_formula(formulas, e.right)
          right = right_label if right_label else stringify_tree(e.right)
          formula = ' '.join((left, e.value.value, right))
        case FunctionNode():
          args = list()
          for arg in e.args:
            arg_label = __find_formula(formulas, arg)
            found = arg_label if arg_label else stringify_tree(arg)
            args.append(found)
          args_str = ', '.join(args)
          formula = f'{e.value.value}({args_str})'
      formulas[label] = e
      entries.append(f'{label} = {formula}')
    print(entries)
  print('\n' + data.format_params(round_digits=ROUND_PARAM_DIGITS))


def __find_formula(formulas: dict[str, Node], node: Node) -> str:
  for key in formulas:
    if formulas[key] is node: return key
  return str()
