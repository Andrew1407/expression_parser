from graphviz import Graph
from types import NoneType
import uuid
from analyzer.tree_nodes import Node, UnaryOperatorNode, BinaryOperatorNode, FunctionNode


def build_tree_graph(tree: Node, name: str, file_path: str, view: bool = True):
  graph = Graph(name=name, filename=file_path)
  add_tree_nodes(graph, tree)
  if view: graph.view()
  else: graph.render()


def add_tree_nodes(graph: Graph, node: Node, parent: str | NoneType = None):
  name = __add_node(graph, node, parent)
  match node:
    case UnaryOperatorNode():
      add_tree_nodes(graph, node.expression, name)
    case BinaryOperatorNode():
      add_tree_nodes(graph, node.left, name)
      add_tree_nodes(graph, node.right, name)
    case FunctionNode():
      for expression in node.args:
        add_tree_nodes(graph, expression, name)


__node_colors = {
  UnaryOperatorNode: 'green3',
  BinaryOperatorNode: 'yellow3',
  FunctionNode: 'purple',
  Node: 'skyblue2',
}


def __add_node(graph: Graph, node: Node, parent: str | NoneType = None) -> str:
  name = str(uuid.uuid1())
  color = __node_colors[node.__class__]
  graph.attr('node', style='filled', color=color)
  graph.node(name=name, label=node.value.value)
  if parent: graph.edge(parent, name)
  return name
