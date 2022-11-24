import os
import json
from typing import Sequence
from parser.tokens import Token
from analyzer.tree_nodes import Node


OUTPUT_DIR = 'dist'
SYNTAX_TREE_PATH = f'{OUTPUT_DIR}/syntax_tree.json'
PARALLEL_TREE_PATH = f'{OUTPUT_DIR}/parallel_tree.json'
TOKEN_LIST_PATH = f'{OUTPUT_DIR}/tokens.json'


def write_syntax_tree(tree: Node):
  if not os.path.exists(OUTPUT_DIR):
    os.mkdir(OUTPUT_DIR)
  with open(SYNTAX_TREE_PATH, 'w') as f:
    f.write(tree.to_json())


def write_parallel_tree(tree: Node):
  if not os.path.exists(OUTPUT_DIR):
    os.mkdir(OUTPUT_DIR)
  with open(PARALLEL_TREE_PATH, 'w') as f:
    f.write(tree.to_json())


def write_tokens(tokens: Sequence[Token]):
  if not os.path.exists(OUTPUT_DIR):
    os.mkdir(OUTPUT_DIR)
  json_list = json.dumps(tuple(tokens), default=lambda o: o.__dict__, indent=2)
  with open(TOKEN_LIST_PATH, 'w') as f:
    f.write(json_list)
