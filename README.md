# Expression parser

[![main workflow badge](https://github.com/andrew1407/expression_parser/actions/workflows/main.yml/badge.svg)](https://github.com/andrew1407/expression_parser/actions)

## Description

The main (entry) script runs a console app expecting an expression input. It uses **[ExpressionParser](./expression_parser/parser/expression_parser.py)** to parse a raw input (string) returning token/error list, and **[SyntaxAnalysisException](./expression_parser/analyzer/syntax_analyzer.py)** to build a syntax tree using parsed tokens (if no parsing exceptions occured). In case of any syntax error it raises a SyntaxAnalysisException reffering to error token. **[Parallel tree module](./expression_parser/parallel_tree)** contails functions for convering a syntax tree into its parallel form; they also optimize operations, open brackets applying minus and reduce unary operations. **[Expression view](./expression_parser/tree_output/expression_view.py)** logs execution results during parsing. **[Equivalent forms](./expression_parser/equivalent_forms/)** module contains commutativity and distributivity expression opearations. **[Dynamic conveyor](./expression_parser/conveyor_simulation/dynamic.py)** simulates calculations for a given expressions allowing to set different layers count and operations time.
<br />
[Unit tests](./test) cover different behavior cases using the mentioned modules. Many valid and invalid test cases can be found there.

## Commands

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

**Install dependencies:**
```bash
pip install -r requirements.txt
```

**Run the script:**
```bash
python main.py
```

**Run tests:**
```bash
python -m unittest
```
