###########################
## Milestone 5 : CS335A ##
######################################
## Submission Date : April 10, 2022 ##
######################################

__author__ = "Group 26, CS335A"
__filename__ = "classes.py"
__description__ = "Helper classes for compiler."


from typing import List


class Format:
    """
    Collection of ANSI escape sequences to format strings
    """

    success: str = "\033[32m"
    fail: str = "\033[91m"
    end: str = "\033[0m"
    underline: str = "\033[4m"


class Node:
    def __init__(
        self,
        name: str = "",
        val: str = "",
        line_num: int = 0,
        type: str = "",
        children: List = [],
        array: List = [],
        func: int = 0,
        level: int = 0,
        ast=None,
        code: List = [],
        update: List = [],
        place: str = "",
        dims: List = [],
        placelist: List = [],
        truelabel: str = "",
        falselabel: str = ""
    ):
        self.name = name
        self.val = val
        self.type = type
        self.line_num = line_num
        self.array = array
        self.func = func
        self.ast = ast
        self.level = level
        self.code = []
        self.update = update
        self.place = place
        self.dims = dims
        self.placelist = placelist
        self.truelabel = truelabel
        self.falselabel = falselabel
        if children:
            self.children = children
        else:
            self.children = []
