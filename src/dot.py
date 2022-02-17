##########################
## Milestone 3 : CS335A ##
########################################
## Submission Date: February 18, 2022 ##
########################################

__author__ = "Group 26, CS335A"
__filename__ = "dot.py"
__description__ = "Generates graph of Parser Automaton."

import pydot
# from datetime import datetime


## Global color encoding
BLUE = "#1e81b0"
GREEN = "#3e9632"
RED = "#cb3d0f"
SHAPE = "circle"

line_nonterminal = "Nonterminals,"
line_terminal = "Terminals,"
line_parsing = "Parsing"

graph = pydot.Dot(graph_type="digraph")
file1 = open("parser.out", "r")
Lines = file1.readlines()

count = 0
node = {}
terminals = []
nonterminals = []
cc = 0
header = 0
# Strips the newline character
for line in Lines:
    # print(header)
    tokens = line.split()

    if len(tokens) > 0 and tokens[0] == line_terminal:
        header = 1
        continue

    if len(tokens) > 0 and tokens[0] == line_nonterminal:
        header = 2
        continue

    if len(tokens) > 0 and tokens[0] == line_parsing:
        header = 3
        continue

    if len(tokens) > 0 and header == 1:
        terminals.append(tokens[0])

    if len(tokens) > 0 and header == 2:
        nonterminals.append(tokens[0])

    if len(tokens) > 0 and tokens[0] == "state":
        count += 1
        name = "I" + tokens[len(tokens) - 1]
        n = pydot.Node(name, shape=SHAPE, color=BLUE)
        node[name] = n


###########
## GRAPH ##
###########

for i in node.values():
    graph.add_node(i)

curr_state = ""
for line in Lines:
    tokens = line.split()

    cc += 1

    if len(tokens) > 0 and tokens[0] == "state":
        curr_state = "I" + tokens[1]

    print(curr_state, "-", cc)
    if cc == 32:
        print(tokens)

    if len(tokens) > 0 and "shift and go to state" in line and tokens[0] != "!":
        if tokens[0] in terminals:
            col = GREEN
        elif tokens[0] in nonterminals:
            col = RED

        graph.add_edge(
            pydot.Edge(
                node[curr_state],
                node["I" + tokens[len(tokens) - 1]],
                label=tokens[0],
                fontcolor=col,
                fontsize="10.0",
                color=col,
            )
        )


## Save graph as image
graph.write_dot("graph.dot")

# curr_date = datetime.now().strftime("%d%M%Y-%H%M%S")
graph.write_png("graph.png")
## Save graph as dot file
# Debugging
# print(terminals)
# print(nonterminals)
