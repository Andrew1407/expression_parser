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

The main (entry) script uses runs console app expecting an expression input. It uses **[ExpressionParser](./parser/expression_parser.py)** to parse raw input (string) returning tokens|errors list, and **[SyntaxAnalysisException](./analyzer/syntax_analyzer.py)** to build a syntax tree using parsed tokens (if no parsing exceptions occured). In case of any syntax error it raises a SyntaxAnalysisException reffering to error token.
<br />
[Unit tests](./test) cover different behavior cases using the mentioned modules. Many valid and invalid test cases can be found there.
