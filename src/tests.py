#!/bin/python3

import subprocess
import sys
import os
import math

from my_box import box_that
from my_color import my_color as color

class Info:
    def __init__(self, line: str, method: str, var: str) -> None:
        self.line = line
        self.method = method
        self.var = var

    def show(self) -> None:
        line = "{}{}".format("Line:".ljust(12), self.line)
        meth = "{}{}".format("Method:".ljust(12), self.method)
        list = [line, meth]
        box, _ = box_that(self.var if self.var else "", list)
        print(box, end='')


def get_create():
    command = "grep -rn '_create*' . | grep -v -e '.py'"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    lines = result.stdout.strip()
    if result.returncode != 0:
        print(f"Error : {result.stderr.strip()}")
    create_array = lines.split("\n")
    return create_array


def get_destroy():
    command = "grep -rn '_destroy*' . | grep -v -e '.py'"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    lines = result.stdout.strip()
    if result.returncode != 0:
        print(f"Error : {result.stderr.strip()}")
    destroy_array = lines.split("\n")
    return destroy_array


def find_word(text: str, search_word: str):
    words = text.split()
    for word in words:
        if search_word in word:
            return word[:word.find(search_word)]
    return None


def find_wordindex(text: str, search_word: str):
    mylist = text.split()
    for i in range(len(mylist)):
        if search_word in mylist[i]:
            return i

def get_infos(array: list[str], search: str):
    ret = []
    for line in array:
        mylist = line.split()
        method = find_word(line, search)
        methodindex = find_wordindex(line, method + search)
        varname = mylist[methodindex - 2] if methodindex > 2 else None

        info = Info(line=mylist[0], method=method, var=varname)
        ret.append(info)
    return ret


def display_log(a: list[str], b: list[str]) -> None:
    if (a is not None):
        icreate_array = get_infos(a, "_create")
        print(f"\n{color.lblue}CREATE{color.r}")
        [i.show() for i in icreate_array]

    if (b is not None):
        idestroy_array = get_infos(b, "_destroy")
        print(f"\n{color.lblue}DESTROY{color.r}")
        [i.show() for i in idestroy_array]


def create_bar(percentage: int, name: str) -> str:

    show_percentage = (str(percentage) + "%").ljust(4) if percentage < 100 else "Done".ljust(4)
    number = math.ceil((percentage / 100) * 20)
    fill = '=' * number
    fill = fill[:-1] + '>' if percentage != 100 else fill
    spaces = ' ' * (20 - (number if percentage != 0 else (number + 1)))

    col = color.red
    col = color.orange if percentage > 33 else col
    col = color.green if percentage > 66 else col
    bar = '[' + col + fill + spaces + color.r + ']'
    ret = f"{show_percentage} {bar} {name}"
    return ret


def process_test(test_status: bool, display: str) -> None:
    CHECKS = "✓✗"
    test_display = "{}{}{}"
    test_display = test_display.format(
        ((color.green + CHECKS[0]) if test_status else (color.red + CHECKS[1])).ljust(10) + color.r,
        display, color.r)
    print(test_display)


def process_tips(results: list[bool], a: list[str], b: list[str]) -> None:
    if (not results[0]):
        print("\n{}Minimal Functions{}".format(color.under, color.r))
        print("For {} {}create{}, you have {} {}destroy{}.".format(
            len(a), color.lblue, color.r, len(b), color.lblue, color.r))
        print("Check with {}--log=full{} to see all your missing destroy.".format(color.bold, color.r))
    if (not results[1]):
        print("\n{}No environnement{}".format(color.under, color.r))
        print("Check if your environnement is {}NULL{} and return 84 if its the case".format(color.lblue, color.r))
    print()

def main() -> None:
    a = 0
    results = []

    create_array = get_create()
    destroy_array = get_destroy()

    if (("--log=full" in sys.argv) and (len(sys.argv) == 2)):
        return display_log(create_array, destroy_array)
    if (("--log=create" in sys.argv) and (len(sys.argv) == 2)):
        return display_log(create_array, None)
    if (("--log=destroy" in sys.argv) and (len(sys.argv) == 2)):
        return display_log(None, destroy_array)

    print("\n==> Graphic Testing\n")

    test_status = len(create_array) == len(destroy_array)
    results.append(test_status)
    process_test(test_status, "Minimal Functions")
    a += 1

    test_status = os.WEXITSTATUS(os.system("env -i ./my_rpg")) == 84
    results.append(test_status)
    process_test(test_status, "No environnement")
    a += 1

    print("\n==> Summary")
    print(create_bar(int((results.count(True) / a) * 100), "Total"))

    print("\n==> Tips")
    process_tips(results, create_array, destroy_array)

if __name__ == "__main__":
    main()