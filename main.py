from expression_parser import ExpressionParser
import dataclasses

@dataclasses.dataclass
class Sas:
  a: int
  b: int

if __name__ =='__main__':
  expression = ' 3 * sin + (asdas45* s/ 8) -r.82 + 8 '
  ep = ExpressionParser(expression)
  print('Tokens:')
  for t in ep.get_tokens(): print(t)
  
  print('\nErros:')
  for e in ep.get_exceptions(): print(e)
