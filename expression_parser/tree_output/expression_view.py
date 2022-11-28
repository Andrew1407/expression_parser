from typing import Sequence, Self
from expression_parser.parser.expression_parser import ParsingExeprion
from expression_parser.parser.tokens import Token
from expression_parser.analyzer.syntax_analyzer import SyntaxAnalysisException
from expression_parser.analyzer.tree_nodes import Node
from . import console_output, file_output


class ExpressionView:
  @staticmethod
  def __method_wrapper(fn=None):
    def decorator(method):
      def wrapper(self, *args, **kwargs):
        if callable(fn): fn(*args, **kwargs)
        return method(self, *args, **kwargs)
      return wrapper
    return decorator
  
  
  @__method_wrapper(console_output.log_tokens)
  @__method_wrapper(file_output.write_tokens)
  def show_tokens(self, tokens: Sequence[Token]): ...


  @__method_wrapper(console_output.log_syntax_tree)
  @__method_wrapper(file_output.write_syntax_tree)
  @__method_wrapper(file_output.show_syntax_tree)
  def show_syntax_tree(self, tree: Node): ...


  @__method_wrapper(console_output.log_parallel_tree)
  @__method_wrapper(file_output.write_parallel_tree)
  @__method_wrapper(file_output.show_parallel_tree)
  def show_parallel_tree(self, tree: Node): ...


  @__method_wrapper(console_output.log_parsing_exception)
  def show_parsing_exceptions(self, message: str, exceptions: ParsingExeprion): ...


  @__method_wrapper(console_output.log_syntax_exception)
  def show_syntax_exception(self, exception: SyntaxAnalysisException): ...
