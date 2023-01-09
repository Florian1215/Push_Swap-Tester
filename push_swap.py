import os
import sys
import random
import subprocess
import math

int_min = -500
int_max = 500

dir_name = 'push_Swap-tester/'
checker_path = f'./{dir_name}checker_Mac'
abs_path = os.path.split(os.path.dirname(__file__))[0]
push_swap_path = f'{abs_path}/push_swap'
checker_bonus_path = f'{abs_path}/checker'

make_file_cmd = 'make'
if os.path.exists('../Makefile'):
    make_file_cmd = 'make -C ../'
os.popen(make_file_cmd).read()

eval_pts = {100: {700: 5, 900: 4, 1100: 3, 1300: 2, 1500: 1}, 500: {5500: 5, 7000: 4, 8500: 3, 10000: 2, 11500: 1}}


# General --------------------------------------------------------
def get_random_number(k_, all_range=False):
    return ' '.join([str(nb) for nb in random.sample(range(int_min, int_max) if all_range else range(0, k_), k=k_)])


def get_pts(n, ct_):
    for max_ins in eval_pts[n]:
        if ct_ < max_ins:
            return eval_pts[n][max_ins]
    return 0


# Color ----------------------------------------------------------
class C:
    GREY = 90
    RED = 91
    GREEN = 92
    YELLOW = 93
    BLUE = 94
    PINK = 95
    CYAN = 96
    NL = False


def print_color(str_, col, nl=True):
    print(f"\033[{col}m {str_}\033[00m", end='\n' if nl else '')
    C.NL = nl


def print_args(ct_, args_check_):
    if '-a' in sys.argv:
        if not ct_:
            print_color(f' {"" if ct_ >= 10 else " "}{ct_}', C.GREY, False)
        print_color(f'  -  {args_check_}', C.GREY)


# Error ----------------------------------------------------------
def error(string_):
    if not C.NL:
        print()
    print_color('Error: ', C.RED, nl=False)
    print_color(string_, C.GREY)


def ko(string_):
    if not C.NL:
        print()
    print_color('\tKO ', C.RED, nl=False)
    print_color(string_, C.GREY)


def cmd_error(args_):
    res = cmd(args_, True)
    if res != "Error\n":
        error(f"With '{args_}' we must have \"Error\", we have '{res}'")
    else:
        print_color("\tOK", C.GREEN, False)


def cmd_nothing_return(args_):
    c = cmd(args_).removesuffix('\n')
    if c:
        error(f"Your program should return nothing with '{args_}', he return '{c}'")
    else:
        print_color("\tOK", C.GREEN, False)


def cmd_parsing(args_):
    if cmd(args_, True, False) == "Error\n":
        error(f"Parsing error with '{args_}'")
    else:
        print_color("\tOK", C.GREEN, False)


def cmd_leaks(args_):
    if os.system(f'leaks -atExit -- {push_swap_path} {args_}') > 0:
        error(f'You have Leaks ! with \'{args_}\'')
        exit()


# CMD ------------------------------------------------------------
def cmd(args_, stderror=False, sterr_msg=True):
    proc = subprocess.Popen(f'{push_swap_path} {args_}', shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE).communicate()
    if stderror:
        if not proc[1] and sterr_msg:
            error('error message must be on stderr')
            return ''
        return proc[1].decode()
    return proc[0].decode()


def cmd_check(args_):
    proc = subprocess.Popen(f'{push_swap_path} {args_} | {checker_path} {args_}', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()
    if proc[1]:
        return proc[1].decode().removesuffix('\n')
    return proc[0].decode().removesuffix('\n')


def cmd_count(args_):
    return len(cmd(args_).split('\n')) - 1


def cmd_all_n(n):
    all_comb = []
    all_count = []
    res = [-1] * n

    def rec(tab, index=0):
        if index >= n:
            if len(set(tab)) == n:
                all_comb.append(' '.join(str(k_) for k_ in tab))
            return
        for i in range(n):
            tab[index] = i
            rec(tab, index + 1)

    rec(res)

    for comb in all_comb:
        check_ = cmd_check(comb)
        if check_ == "KO":
            ko(f"don't sort '{comb}'")
        elif check_ == 'Error':
            error('checker_Mac return Error')
        else:
            ct_ = len(cmd(comb).split('\n')) - 1
            all_count.append(ct_)
            if n == 5 and ct_ > 12:
                ko(f"you sort in more than 12 instructions '{comb}'")
            elif n == 3 and ct_ > 3:
                ko(f"you sort in more than 3 instructions '{comb}'")
            elif n == 3 or all_comb.index(comb) % 15 == 0:
                print_color("\tOK", C.GREEN, False)
    return all_count


# CODE ---------------------------------------------------------------

if not os.path.exists(push_swap_path) or not os.path.exists(checker_path):
    error(f'don\'t find {push_swap_path} or {checker_path}')
    exit()

if 'evaluating' in sys.argv:
    print_color("\n→ Error management:", C.BLUE, False)

    print_color("\n  Non numeric", C.PINK)
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

    print_color("\n  Duplicate args", C.PINK)
    cmd_error("2 6 3 6")
    cmd_error("6 6 3")
    cmd_error("3 6 3")
    cmd_error("1 6 8 4 2 3 1")
    cmd_error("-4 2 6 7 9 11 11 15 86 1848")
    cmd_error("-4 2 6 7 9 11 15 86 1848 1848")

    print_color("\n  Max INT", C.PINK)
    cmd_error("1 2147483648 8 4 2 3")
    cmd_error("1 6 8 2147483649 2 3")
    cmd_error("1 6 -2147483649 4 2 3")
    cmd_error("-2147483649 1 6 8 4 2 3")

    print_color("\n  Nothing to return", C.PINK)
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

    print_color("\n  Parsing", C.PINK)
    cmd_error('""')
    cmd_parsing('"0 5 8 9"')
    cmd_parsing('"0 5 1 9 2"')
    cmd_parsing('"5 6 8 9"')
    cmd_parsing('"9 5 8 -1288"')
    if '-s' in sys.argv or '--strict' in sys.argv:
        cmd_error('0 5 8 9 ""')
        cmd_error('0 "" 95 -11')
        cmd_error('"" 8 -1288')
        cmd_error('8 -12 ""')
        cmd_parsing('"0 5 9" 8')
        cmd_parsing('0 5 1 "9 2"')
        cmd_parsing('"5" 6 8 9')
        cmd_parsing('"9 5" 8 -1288')

    print_color("\n\n→ Simple version:", C.BLUE, False)

    print_color("\n  3 args", C.PINK)
    cmd_all_n(3)
    print_color("\n  5 args", C.PINK)
    cmd_all_n(5)

    print_color("\n\n→ Middle version:", C.BLUE, False)

    for length in (100, 500):
        print_color(f"\n  {length} random", C.PINK)
        all_ct = []
        for _ in range(100 if length == 100 else 50):
            args = get_random_number(length)
            check = cmd_check(args)
            if check == 'KO':
                ko(f"don't sort '{args}'")
            elif check == 'Error':
                error('checker_Mac return Error')
            else:
                all_ct.append(cmd_count(args))
        if all_ct:
            if 0 in all_ct:
                all_ct.remove(0)
            print_color(f'\tmean {int(sum(all_ct) / len(all_ct))} - {get_pts(length, int(sum(all_ct) / len(all_ct)))} pts\n', C.YELLOW)
            print_color(f'\tmin {min(all_ct)} - {get_pts(length, min(all_ct))} pts', C.BLUE)
            print_color(f'\tmax {max(all_ct)} - {get_pts(length, min(all_ct))} pts', C.CYAN)
        else:
            ko(f'you KO all you sort {length} args')

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
    cmd_leaks('"0 5 8 9"')
    cmd_leaks('"0 5 1 9 2"')
    cmd_leaks('"5 6 8 9"')
    cmd_leaks('"9 5 8 -1288"')
    cmd_leaks('""')
    if '-s' in sys.argv or '--strict' in sys.argv:
        cmd_leaks('"0 5 9" 8')
        cmd_leaks('0 5 1 "9 2"')
        cmd_leaks('"5" 6 8 9')
        cmd_leaks('"9 5" 8 -1288')
        cmd_leaks('"" 8 -1288')
        cmd_leaks('8 -12 ""')
        cmd_leaks('-2 "" 4 ""')

    for k in (3, 5, 10, 50, 100, 500):
        for _ in range(10):
            cmd_leaks(get_random_number(k))

    print_color("\tOK", C.GREEN, False)
    print_color('you have no leaks !\n', C.GREY)

elif 'random' in sys.argv:
    print(get_random_number(int(sys.argv[2]) if len(sys.argv) >= 3 else 100, True))
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
                print_color("\tKO", C.RED, '-a' not in sys.argv)
                print_args(False, args_check)
            else:
                ct = cmd_count(args_check)
                print_color("\tOK", C.GREEN, False)
                if '-a' in sys.argv:
                    print_args(ct, args_check)
                else:
                    print_color(f' sort in {ct}', C.GREY)
                all_ct.append(ct)
    if n_time > 1 and all_ct:
        print_color(f'\nmean = {int(sum(all_ct) / len(all_ct))}{f" ({get_pts(length_args, int(sum(all_ct) / len(all_ct)))} pts)" if length_args in eval_pts else ""}\n', C.YELLOW)
        if 0 in all_ct:
            all_ct.remove(0)
        print_color(f'min = {min(all_ct)}{f" ({get_pts(length_args, min(all_ct))} pts)" if length_args in eval_pts else ""}', C.BLUE)
        print_color(f'max = {max(all_ct)}{f" ({get_pts(length_args, min(all_ct))} pts)" if length_args in eval_pts else ""}', C.CYAN)
    elif length_args in eval_pts and all_ct:
        print_color(f'\t\t{get_pts(length_args, min(all_ct))} pts', C.BLUE)
