# CS335A Compiler Design: Course Project

Our SIT triplet is (Go, Python, MIPS).

## Table of Contents

1. [Timeline](#i-timeline)
2. [Usage Guidelines](#ii-usage-guidelines)
3. [Group Members](#iii-group-members)
4. [Acknowledgement](#iv-acknowledgement)

## i. Timeline

- [x] Milestone 1 : Specs 
    - _Due on: 24.01.2022_
    - In this milestone, we had to provide the details of our Compiler. 
    - Deliverables
        - docs/specs.pdf`
- [ ] Milestone 2 : Scanner
    - _Due on: 01.02.2022_
    - In this milestone, we had to construct a scanner for the source language to output the tokens in a tabular form.
    - Deliverables
        - `src/lexer.py`
        - `tests/scanner/`
        - `docs/lexer.md`
        - `Makefile`


## ii. Usage Guidelines

Clone the repository and navigate into the directory

```bash
git clone git@github.com:gurbaaz27/CS335-Course-Project.git
cd CS335-Course-Project/
```

#### a. Milestone 2: Scanner

There are 5 test-cases present in `tests/scanner/` directory.
To run the test cases, simply run

```bash
make test=<test_num>
## For example,
make test=2
```

In case no test variable is mentioned,`make` defaults to `test=1`, i.e.

```bash
make ## is equivalent to
make test=1
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
