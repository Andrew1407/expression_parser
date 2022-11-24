import os
from analyzer.tree_nodes import Node
from .graph_builder import build_tree_graph


SYNTAX_TREE_PATH = 'dist/syntax_tree'
PARALLEL_TREE_PATH = 'dist/parallel_tree'


def show_syntax_tree(tree: Node):
  if not os.path.exists('dist'):
    os.mkdir('dist')
  build_tree_graph(tree, 'syntax_tree', SYNTAX_TREE_PATH)


def show_parallel_tree(tree: Node):
  if not os.path.exists('dist'):
    os.mkdir('dist')
  build_tree_graph(tree, 'parallel_tree', PARALLEL_TREE_PATH)
