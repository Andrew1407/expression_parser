from typing import Callable
from copy import deepcopy
from expression_parser.analyzer.tree_nodes import Node
from expression_parser.parallel_tree.optimizer_tools import open_brackets


def apply_minus_copy_wrapper(fn: Callable[[Node], Node]) -> Callable[[Node], Node]:
  def wrapper(node: Node) -> Node:
    copied = open_brackets(deepcopy(node))
    return fn(copied)
  return wrapper
