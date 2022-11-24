from typing import Sequence
from parser.expression_parser import ParsingExeprion
from parser.tokens import Token
from analyzer.syntax_analyzer import SyntaxAnalysisException
from analyzer.tree_nodes import Node
from . import console_output, file_output, graph_view


def method_wrapper(fn=None):
  def decorator(method):
    def wrapper(self, *args, **kwars):
      if callable(fn): fn(*args, **kwars)
      return method(self, *args, **kwars)
    return wrapper
  return decorator


class ExpressionView:
  @method_wrapper(console_output.log_tokens)
  @method_wrapper(file_output.write_tokens)
  def show_tokens(self, tokens: Sequence[Token]): ...


  @method_wrapper(console_output.log_syntax_tree)
  @method_wrapper(file_output.write_syntax_tree)
  @method_wrapper(graph_view.show_syntax_tree)
  def show_syntax_tree(self, tree: Node): ...


  @method_wrapper(console_output.log_parallel_tree)
  @method_wrapper(file_output.write_parallel_tree)
  @method_wrapper(graph_view.show_parallel_tree)
  def show_parallel_tree(self, tree: Node): ...


  @method_wrapper(console_output.log_parsing_exception)
  def show_parsing_exceptions(self, message: str, exceptions: ParsingExeprion): ...


  @method_wrapper(console_output.log_syntax_exception)
  def show_syntax_exception(self, exception: SyntaxAnalysisException): ...
