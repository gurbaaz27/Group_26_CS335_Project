# CS335A Compiler Design: Course Project

Our SIT triplet is (Go, Python, MIPS).

## Table of Contents

1. [Timeline](#i-timeline)
2. [Usage Guidelines](#ii-usage-guidelines)
    - [Scanner](#a-milestone-2-scanner)
    - [Parser](#b-milestone-3-parser)
    - [Semantic Analysis](#c-milestone-4-semantic-analysis)
    - [Activation Record and Intermediate Code Generation](#d-milestone-5-activation-record-and-intermediate-code-generation)
    - [The Destination](#e-milestone-6-the-destination)
3. [Group Members](#iii-group-members)
4. [Acknowledgement](#iv-acknowledgement)

## i. Timeline

- [x] Milestone 1 : Specs 
    - Due on: 24.01.2022
    - In this milestone, we had to provide the details of our Compiler. 
    - Deliverables
        - `docs/specs.pdf`
- [x] Milestone 2 : Scanner
    - Due on: 01.02.2022
    - In this milestone, we had to construct a scanner for the source language to output the tokens in a tabular form.
    - Deliverables
        - `src/lexer.py`
        - `tests/scanner/`
        - `docs/lexer.md`
        - `Makefile`
- [x] Milestone 3 : Parser
    - Due on: 18.02.2022
    - In this milestone, you have to develop a parser for the source language that outputs the Parser Automaton in a graphical form.
    - Deliverables
        - `src/parser.py`
        - `src/dot.py`
        - `tests/parser/`
        - `docs/parser.md`
        - `Makefile` 
- [x] Milestone 4 : Semantic Analysis
    - Due on: 28.03.2022
    - In this milestone, you extend the project to perform semantic analysis. The goal is to convert your program into an AST Representation to be used by later stages (Intermediate and Final code generation, optimization, etc.).
    - Deliverables
        - `src/parser.py`
        - `src/utils.py`
        - `src/ast_plot.png`
        - `src/ast.dot`
        - `Makefile`
- [x] Milestone 5: Activation Record and Intermediate Code Generation
    - Due on: 10.04.2022
    - Now that you can create AST and Symbol Table for a semantically meaningful program, it is time to generate Intermediate code (3-address code, 3AC) with support for run-time activations.
    - Deliverables
        - `src/parser.py`
        - `src/utils.py`
        - `src/classes.py`
        - `Makefile`
- [ ] Milestone 6: The Destination
    - Due on: 22.04.2022
    - In this last part of the project, you will generate code for the target assembly. 
    - Deliverables
        - `src/parser.py`
        - `Makefile`


## ii. Usage Guidelines

Clone the repository, navigate into the directory and install the dependencies

```bash
git clone git@github.com:gurbaaz27/CS335-Course-Project.git
cd CS335-Course-Project/
pip install -r requirements.txt ## or pip3, according to your system
```

### a. Milestone 2: Scanner

There are 5 test-cases present in `tests/scanner/` directory.
To run the test cases, simply run

```bash
make scanner test=<test_num>
## For example,
make scanner test=2
```

In case no test variable is mentioned,`make` defaults to `test=1`, i.e.

```bash
make scanner ## is equivalent to
make scanner test=1
```

In case you want to run all test-cases at once, run

```bash
make scanner-all
```

If you do not have `make` installed, you can simply run the python script using

```bash
python src/lexer.py tests/scanner/<test_num>.go ## or python3, according to your system
## For example,
python src/lexer.py tests/scanner/2.go
```

> __*NOTE 1*__ : *We do not print COMMENT and NEWLINE in our output, since they have no role in parser.*

> __*NOTE 2*__ : *We have purposely added an illegal character in 5th test-case, which should result our lexer throw an error message on encountering that character(s).*

### b. Milestone 3: Parser

There are 5 test-cases present in `tests/parser/` directory.
To run the test cases, simply run

```bash
make parser test=<test_num>
## For example,
make parser test=2
```

In case no test variable is mentioned,`make` defaults to `test=1`, i.e.

```bash
make parser ## is equivalent to
make parser test=1
```

If you do not have `make` installed, you can simply run the python script using

```bash
python src/parser.py tests/parser/<test_num>.go ## or python3, according to your system
## For example,
python src/parser.py tests/parser/2.go
```

This will generate `src/parser.out` and `src/parsetab.py` files and generate dot file named `<test_num>.dot`

Before moving to next test case, make sure to clean the `src/` folder using

```bash
make clean ## or
rm -rf src/parser.out
rm -rf src/parsetab.py
```

To generate graph from `dot` file, install `graphviz`. For Ubuntu, you can use

```bash
sudo apt install graphviz
```

and make graph using

```bash
make graph test=<test_num> ## or
dot -Tpdf <test_num>.dot -o <test_num>.pdf
```

> __*NOTE*__ : *We have purposely added an illegal syntx in 5th test-case, which should result our parser throw an error message.*

### c. Milestone 4: Semantic Analysis

There are 5 test-cases present in `tests/semantic/` directory.
To run the test cases, simply run

```bash
make semantic test=<test_num>
## For example,
make semantic test=2
```

In case no test variable is mentioned,`make` defaults to `test=1`, i.e.

```bash
make semantic ## is equivalent to
make semantic test=1
```

If you do not have `make` installed, you can simply run the python script using

```bash
python src/parser.py tests/semantic/<test_num>.go ## or python3, according to your system
## For example,
python src/parser.py tests/semantic/2.go
```

> __*NOTE*__ : *We have purposely added wrong semantic in 3rd testcase, which should result our semantic analyser throw an error message.*

### d. Milestone 5: Activation Record and Intermediate Code Generation

There are 5 test-cases present in `tests/3ac/` directory.
To run the test cases, simply run

```bash
make ir test=<test_num>
## For example,
make ir test=2
```

In case no test variable is mentioned,`make` defaults to `test=1`, i.e.

```bash
make ir ## is equivalent to
make ir test=1
```

If you do not have `make` installed, you can simply run the python script using

```bash
python src/parser.py tests/3ac/<test_num>.go ## or python3, according to your system
## For example,
python src/parser.py tests/3ac/2.go
```

### e. Milestone 6: The Destination

There are 5 test-cases present in `tests/final/` directory.
To run the test cases, simply run

```bash
make final test=<test_num>
## For example,
make final test=2
```

In case no test variable is mentioned,`make` defaults to `test=1`, i.e.

```bash
make final ## is equivalent to
make final test=1
```

If you do not have `make` installed, you can simply run the python script using

```bash
python src/parser.py tests/final/<test_num>.go ## or python3, according to your system
## For example,
python src/parser.py tests/final/2.go
```

## iii. Group Members

Group Number: `26`

- [Anshumann](https://github.com/anshmn) (190162)
- [Antreev Singh Brar](https://github.com/antreev-brar) (190163)
- [Dipanshu Garg](https://github.com/dipanshu124) (190306)
- [Gurbaaz Singh Nandra](https://github.com/gurbaaz27) (190349)

## iv. Acknowledgement

- [The Go Programming Language Specification](https://go.dev/ref/spec)
- [PLY (Python Lex-Yacc)](https://www.dabeaz.com/ply/ply.html)
- [regex101: build, test, and debug regex](https://regex101.com/)
