import os
import json
from typing import Sequence
from expression_parser.parser.tokens import Token
from expression_parser.analyzer.tree_nodes import Node
from .graph_builder import build_tree_graph


OUTPUT_DIR = 'dist'
SYNTAX_TREE_PATH = f'{OUTPUT_DIR}/syntax_tree'
PARALLEL_TREE_PATH = f'{OUTPUT_DIR}/parallel_tree'
TOKEN_LIST_PATH = f'{OUTPUT_DIR}/tokens'
DISTRIBUTIVE_FORM_PATH = f'{OUTPUT_DIR}/distributive'
COMMUTATIVE_FORM_PATH = f'{OUTPUT_DIR}/commutative'


def dist_check(fn):
  def wrapper(*args, **kwargs):
    if not os.path.exists(OUTPUT_DIR):
      os.mkdir(OUTPUT_DIR)
    fn(*args, **kwargs)
  return wrapper


@dist_check
def write_syntax_tree(tree: Node):
  with open(SYNTAX_TREE_PATH + '.json', 'w') as f:
    f.write(tree.to_json())


@dist_check
def write_parallel_tree(tree: Node):
  with open(PARALLEL_TREE_PATH + '.json', 'w') as f:
    f.write(tree.to_json())


@dist_check
def write_tokens(tokens: Sequence[Token]):
  json_list = json.dumps(tuple(tokens), default=lambda o: o.__dict__, indent=2)
  with open(TOKEN_LIST_PATH + '.json', 'w') as f:
    f.write(json_list)


@dist_check
def show_syntax_tree(tree: Node):
  build_tree_graph(tree, 'syntax_tree', SYNTAX_TREE_PATH)


@dist_check
def show_parallel_tree(tree: Node):
  build_tree_graph(tree, 'parallel_tree', PARALLEL_TREE_PATH)
