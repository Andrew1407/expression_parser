import os
from analyzer.tree_nodes import Node
from .graph_builder import build_tree_graph


OUTPUT_DIR = 'dist'
SYNTAX_TREE_PATH = f'{OUTPUT_DIR}/syntax_tree'
PARALLEL_TREE_PATH = f'{OUTPUT_DIR}/parallel_tree'


def show_syntax_tree(tree: Node):
  if not os.path.exists(OUTPUT_DIR):
    os.mkdir(OUTPUT_DIR)
  build_tree_graph(tree, 'syntax_tree', SYNTAX_TREE_PATH)


def show_parallel_tree(tree: Node):
  if not os.path.exists(OUTPUT_DIR):
    os.mkdir(OUTPUT_DIR)
  build_tree_graph(tree, 'parallel_tree', PARALLEL_TREE_PATH)
