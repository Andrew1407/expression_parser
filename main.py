from expression_parser.tree_output.expression_view import ExpressionView
from expression_data_builder import ExpressionDataBuilder


class ConsoleInputClient:
  def __init__(self, data_builder: ExpressionDataBuilder):
    self.__builder: ExpressionDataBuilder = data_builder
  

  def pass_input(self, expression: str):
    if expression:
      self.__builder.exceptions_wrapper(self.__parse_expression, expression)


  def __parse_expression(self, expression: str):
    tokens = self.__builder.build_token_list(expression)
    tree = self.__builder.build_syntax_tree(tokens)
    distributive_forms, commutative_forms = self.__builder.build_equivalent_forms(tree)
    self.__builder.build_conveyor_simulations(tree, distributive_forms, commutative_forms)

  
if __name__ == '__main__':
  expression_view = ExpressionView()
  data_builder = ExpressionDataBuilder(expression_view)
  input_client = ConsoleInputClient(data_builder)

  while True:
    try:
      expression = input('> ')
      input_client.pass_input(expression)
    except (KeyboardInterrupt, EOFError):
      print()
      break
