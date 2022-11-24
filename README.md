# Expression parser

**Create venv:**
```bash
python -m venv venv
```

**Activate venv:**
```bash
source venv/bin/activate
```

**Dectivate venv:**
```bash
deactivate
```

**Run the script:**
```bash
python main.py
```

**Run tests:**
```bash
python -m unittest
```

The main (entry) script runs a console app expecting an expression input. It uses **[ExpressionParser](./parser/expression_parser.py)** to parse a raw input (string) returning token/error list, and **[SyntaxAnalysisException](./analyzer/syntax_analyzer.py)** to build a syntax tree using parsed tokens (if no parsing exceptions occured). In case of any syntax error it raises a SyntaxAnalysisException reffering to error token. **[Parallel tree module](./parallel_tree)** contails functions for convering a syntax tree into its parallel form; they also optimize operations, open brackets applying minus and reduce unary operations. **[Expression view](./tree_output/expression_view.py)** logs execution results during parsing.
<br />
[Unit tests](./test) cover different behavior cases using the mentioned modules. Many valid and invalid test cases can be found there.
