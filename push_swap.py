import os
import sys
import random
import subprocess
import math

int_min = -2147483648
int_max = 2147483647

dir_name = 'push_Swap-tester/'
checker_path = f'./{dir_name}checker_Mac'
abs_path = os.path.split(os.path.dirname(__file__))[0]
push_swap_path = f'{abs_path}/push_swap'
checker_bonus_path = f'{abs_path}/checker'

make_file_cmd = 'make'
if os.path.exists('../Makefile'):
    make_file_cmd = 'make -C ../'
os.popen(make_file_cmd).read()

eval_pts = {100: {'pts': {700: 5, 900: 4, 1100: 3, 1300: 2, 1500: 1}, 'max': -1}, 500: {'pts': {5500: 5, 7000: 4, 8500: 3, 10000: 2, 11500: 1}, 'max': -1}}


# General --------------------------------------------------------
def get_random_number(k):
    return ' '.join([str(nb) for nb in random.sample(range(0, k), k=k)])


def get_pts(n, ct):
    for max_ins in eval_pts[n]['pts']:
        if ct < max_ins:
            return eval_pts[n]['pts'][max_ins]
    return 0


# Color ----------------------------------------------------------
def print_color(str, col, nl=True):
    print(f"\033[{col}m {str}\033[00m", end='\n' if nl else '')


class C:
    GREY = 90
    RED = 91
    GREEN = 92
    YELLOW = 93
    BLUE = 94
    PINK = 95
    CYAN = 96


# Error ----------------------------------------------------------
def error(string_):
    print_color('Error: ', C.RED, nl=False)
    print_color(string_, C.GREY)


def cmd_error(args):
    res = cmd(args, True)
    if res != "Error\n":
        print()
        error(f"With '{args}' we must have \"Error\", we have '{res}'")
    else:
        print_color("\tOK", C.GREEN, False)


def cmd_nothing_return(args):
    if cmd(args):
        print()
        error(f"Your program should return nothing, he return '{args}'")
    else:
        print_color("\tOK", C.GREEN, False)


def cmd_parsing(args):
    if cmd(args) == "Error\n":
        print()
        error(f"Parsing error with '{args}'")
    else:
        print_color("\tOK", C.GREEN, False)


def cmd_leaks(args):
    if os.system(f'leaks -atExit -- {push_swap_path} {args}') > 0:
        error(f'You have Leaks ! with \'{args}\'')
        exit()


# CMD ------------------------------------------------------------
def cmd(args, stderror=False):
    proc = subprocess.Popen([push_swap_path, args], stderr=subprocess.PIPE, stdout=subprocess.PIPE).communicate()
    if stderror:
        if not proc[1]:
            error('error message must be on stdout')
            return ''
        return proc[1].decode()
    return proc[0].decode()


def cmd_check(args):
    proc = subprocess.Popen(f'{push_swap_path} {args} | {checker_path} {args}', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()
    if proc[1]:
        return proc[1].decode().removesuffix('\n')
    return proc[0].decode().removesuffix('\n')


def cmd_count(args):
    return len(cmd(args).split('\n')) - 1


def cmd_all_n(n):
    all_comb = []
    all_count = []
    res = [-1] * n

    def rec(tab, index=0):
        if index >= n:
            if len(set(tab)) == n:
                all_comb.append(' '.join(str(k) for k in tab))
            return
        for i in range(n):
            tab[index] = i
            rec(tab, index + 1)

    rec(res)
    nl = False

    for comb in all_comb:
        check = cmd_check(comb)
        if check == "KO":
            if nl:
                print()
            error(f"\tKO don't sort '{comb}'")
            nl = False
        elif check == 'Error':
            if nl:
                print()
            error('checker_Mac return Error')
            nl = False
        else:
            ct = len(cmd(comb).split('\n')) - 1
            all_count.append(ct)
            if n == 5 and ct > 12:
                if nl:
                    print()
                error(f"\tKO you sort in more than 12 instructions '{comb}'")
                nl = False
            elif n == 3 and ct > 3:
                if nl:
                    print()
                error(f"\tKO you sort in more than 3 instructions '{comb}'")
                nl = False
            elif n == 3 or all_comb.index(comb) % 20 == 0:
                print_color("\tOK", C.GREEN, False)
                nl = True
    return all_count


def cmd_middle(n):
    args = get_random_number(n)
    check = cmd_check(args)
    if check == 'KO':
        error(f"\tKO: don't sort '{args}'")
    elif check == 'Error':
        error('checker_Mac return Error')
    else:
        ct = cmd_count(args)
        pt = get_pts(n, ct)
        if eval_pts[n]['max'] < pt:
            eval_pts[n]['max'] = pt
            print_color('\tOK', C.GREEN, False)
            print_color(f'sort in {ct} - {pt} pts', C.GREY)
            if '-a' in sys.argv:
                print(f'ARGS = {args}')


# CODE ---------------------------------------------------------------

if not os.path.exists(push_swap_path) or not os.path.exists(checker_path):
    error(f'don\'t find {push_swap_path} or {checker_path}')
    exit()

if 'evaluating' in sys.argv:
    print_color("\n→ Error management:", C.BLUE)

    print_color("  Non numeric", C.PINK)
    cmd_error("559 3 sdf9")
    cmd_error("5hj 45 6 4")
    cmd_error("5 45 6hj 4")
    cmd_error("5 45 6 4 a")
    cmd_error("5 45 48 s")
    cmd_error("69 425 one 1")
    cmd_error("5 4-5 6 58")
    cmd_error("2 45 6 -")
    cmd_error("2 - 6 3")
    cmd_error("- 6 3")
    cmd_error("1-2 6 3")
    cmd_error("-158 6 3-5")

    print()
    print_color("  Duplicate args", C.PINK)
    cmd_error("2 6 3 6")
    cmd_error("6 6 3")
    cmd_error("3 6 3")
    cmd_error("1 6 8 4 2 3 1")
    cmd_error("-4 2 6 7 9 11 11 15 86 1848")
    cmd_error("-4 2 6 7 9 11 15 86 1848 1848")

    print()
    print_color("  Max INT", C.PINK)
    cmd_error("1 2147483648 8 4 2 3")
    cmd_error("1 6 8 2147483649 2 3")
    cmd_error("1 6 -2147483649 4 2 3")
    cmd_error("-2147483649 1 6 8 4 2 3")

    print()
    print_color("  Nothing to return", C.PINK)
    cmd_nothing_return("")
    cmd_nothing_return("42")
    cmd_nothing_return("30")
    cmd_nothing_return("-5")
    cmd_nothing_return("0 1 2 3")
    cmd_nothing_return("-185 26 48 8546")
    cmd_nothing_return("0 1 2 3 4 5 6 7 8 9 10 11")
    cmd_nothing_return("-554949 -2549 -695 15 45948 545498")
    cmd_nothing_return("548 9898")
    cmd_nothing_return("1 2")

    print()
    print_color("  Parsing", C.PINK)
    cmd_error('""')
    cmd_parsing('"0 5 8 9"')
    cmd_parsing('"0 5 1 9 2"')
    cmd_parsing('"5 6 8 9"')
    cmd_parsing('"9 5 8 -1288"')

    cmd_parsing('"0 5 9" 8')
    cmd_parsing('0 5 1 "9 2"')
    cmd_parsing('"5" 6 8 9')
    cmd_parsing('"9 5" 8 -1288')

    print_color("\n\n→ Simple version:", C.BLUE)

    print_color("  3 args", C.PINK)
    cmd_all_n(3)
    print()
    print_color("  5 args", C.PINK)
    cmd_all_n(5)

    print_color("\n\n→ Middle version:", C.BLUE)

    print_color("  100 random", C.PINK)
    for _ in range(100):
        cmd_middle(100)

    print()
    print_color("  500 random", C.PINK)
    for _ in range(50):
        cmd_middle(500)
elif 'leaks' in sys.argv:

    print_color("→ Leaks Error\n", C.BLUE)
    cmd_leaks("559 3 sdf9")
    cmd_leaks("5hj 45 6 4")
    cmd_leaks("5 45 6hj 4")
    cmd_leaks("5 45 6 4 a")
    cmd_leaks("5 45 48 s")
    cmd_leaks("69 425 one 1")
    cmd_leaks("5 4-5 6 58")
    cmd_leaks("2 45 6 -")
    cmd_leaks("2 - 6 3")
    cmd_leaks("- 6 3")
    cmd_leaks("2 6 3 6")
    cmd_leaks("6 6 3")
    cmd_leaks("3 6 3")
    cmd_leaks("1 6 8 4 2 3 1")
    cmd_leaks("-4 2 6 7 9 11 11 15 86 1848")
    cmd_leaks("-4 2 6 7 9 11 15 86 1848 1848")
    cmd_leaks("1 2147483648 8 4 2 3")
    cmd_leaks("1 6 8 2147483649 2 3")
    cmd_leaks("1 6 -2147483649 4 2 3")
    cmd_leaks("-2147483649 1 6 8 4 2 3")
    cmd_leaks("")
    cmd_leaks("42")
    cmd_leaks("30")
    cmd_leaks("-5")
    cmd_leaks("0 1 2 3")
    cmd_leaks("-185 26 48 8546")
    cmd_leaks("0 1 2 3 4 5 6 7 8 9 10 11")
    cmd_leaks("-554949 -2549 -695 15 45948 545498")
    cmd_leaks("548 9898")
    cmd_leaks("1 2")
    cmd_leaks('""')
    cmd_leaks('"0 5 8 9"')
    cmd_leaks('"0 5 1 9 2"')
    cmd_leaks('"5 6 8 9"')
    cmd_leaks('"9 5 8 -1288"')
    cmd_leaks('"0 5 9" 8')
    cmd_leaks('0 5 1 "9 2"')
    cmd_leaks('"5" 6 8 9')
    cmd_leaks('"9 5" 8 -1288')

    for k in (3, 5, 10, 50, 100, 500):
        cmd_leaks(get_random_number(k))

    print_color("\tOK", C.GREEN, False)
    print_color('you have no leaks !\n', C.GREY)

else:
    length_args = int(sys.argv[1]) if len(sys.argv) >= 2 and sys.argv[1].isdigit() else 100
    n_time = int(sys.argv[2]) if len(sys.argv) >= 3 and sys.argv[2].isdigit() else 1
    if 'all' in sys.argv and length_args < 8:
        n_time = math.factorial(length_args)
    all_args = []
    all_ct = []
    for _ in range(n_time):
        while True:
            args_check = get_random_number(length_args)
            if args_check not in all_args:
                all_args.append(args_check)
                break
        check = cmd_check(args_check)
        if check == 'Error':
            error('checker_Mac return Error')
        else:
            if check == "KO":
                print_color("\tKO", C.RED, False)
                if '-a' in sys.argv:
                    print_color(f' {"" if ct >= 10 else " "}{ct}  -  {args_check}', C.GREY)
                else:
                    print()
            else:
                ct = cmd_count(args_check)
                print_color("\tOK", C.GREEN, False)
                if '-a' in sys.argv:
                    print_color(f' {"" if ct >= 10 else " "}{ct}  -  {args_check}', C.GREY)
                else:
                    print_color(f' sort in {ct}', C.GREY)
                all_ct.append(ct)
    if n_time > 1:
        print_color(f'\nmean = {int(sum(all_ct) / len(all_ct))}{f" ({get_pts(length_args, int(sum(all_ct) / len(all_ct)))} pts)" if length_args in eval_pts else ""}\n', C.YELLOW)
        if 0 in all_ct:
            all_ct.remove(0)
        print_color(f'min = {min(all_ct)}{f" ({get_pts(length_args, min(all_ct))} pts)" if length_args in eval_pts else ""}', C.BLUE)
        print_color(f'max = {max(all_ct)}{f" ({get_pts(length_args, min(all_ct))} pts)" if length_args in eval_pts else ""}', C.CYAN)
    elif length_args in eval_pts and all_ct:
        print_color(f'\t\t{get_pts(length_args, min(all_ct))} pts', C.BLUE)
