import os
from analyzer.tree_nodes import Node


SYNTAX_TREE_PATH = 'dist/syntax_tree.json'
PARALLEL_TREE_PATH = 'dist/parallel_tree.json'


def write_syntax_tree(tree: Node):
  if not os.path.exists('dist'):
    os.mkdir('dist')
  f = open(SYNTAX_TREE_PATH, 'w')
  f.write(tree.to_json())
  f.close()


def write_parallel_tree(tree: Node):
  if not os.path.exists('dist'):
    os.mkdir('dist')
  f = open(PARALLEL_TREE_PATH, 'w')
  f.write(tree.to_json())
  f.close()
