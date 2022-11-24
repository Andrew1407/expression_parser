from typing import Sequence
from parser.expression_parser import ParsingExeprion
from parser.tokens import Token
from analyzer.syntax_analyzer import SyntaxAnalysisException
from analyzer.tree_nodes import Node


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
