import os
import sys
import math
import random
import subprocess

int_min = -500
int_max = 500


# checker_name = 'checker_Mac'
checker_name = 'checker_linux'

checker_path = f'./Push_Swap-Tester/{checker_name}'
push_swap_path = f'./push_swap'
checker_bonus_path = f'./checker'

make_file_cmd = 'make'
os.popen(make_file_cmd).read()

eval_pts = {100: {700: 5, 900: 4, 1100: 3, 1300: 2, 1500: 1}, 500: {5500: 5, 7000: 4, 8500: 3, 10000: 2, 11500: 1}}



# General -----------------------------------------------------------
def get_random_number(k_, all_range=False):
    return ' '.join([str(nb) for nb in random.sample(range(int_min, int_max) if all_range else range(0, k_), k=k_)])


def get_pts(n, ct_):
    for max_ins in eval_pts[n]:
        if ct_ < max_ins:
            return eval_pts[n][max_ins]
    return 0


def remove_suffix(string):
    if string and string[-1] == '\n':
        return string[:-1]
    return string


# Color -------------------------------------------------------------
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


# Error -------------------------------------------------------------
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
    for boolean in (False, True):
        c = remove_suffix(cmd(args_, boolean, False))
        if c:
            error(f"Your program should return nothing with '{args_}', he return '{c}'")
            break
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


# CMD ---------------------------------------------------------------
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
        return remove_suffix(proc[1].decode())
    return remove_suffix(proc[0].decode())


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


# CODE --------------------------------------------------------------
if not os.path.exists(push_swap_path) or not os.path.exists(checker_path):
    error(f'don\'t find {push_swap_path} or {checker_path}')
    exit()

checks = {'Non numeric': {'func': cmd_error,
                          'test': ['559 3 sdf9', '5hj 45 6 4', '5 45 6hj 4', '5 45 6 4 a', '5 45 48 s', '69 425 one 1',
                                   '5 4-5 6 58', '2 45 6 -', '2 - 6 3', '- 6 3', '1-2 6 3', '-158 6 3-5', '--15 59 66',
                                   '1 5 9 44 + 2 4', '1 2- 3', '++15 214 3', '7 2+ 3', '""', '8 -12 ""', '"" 8 -1288',
                                   '0 "" 95 -11', '0 5 8 9 ""']},
          'Duplicate args': {'func': cmd_error,
                             'test': ['2 6 3 6', '1 1 2 4 5', '6 6 3', '3 6 3', '1 6 8 4 2 3 +1', '-4 2 6 7 9 11 11 15 86 1848', '4 2 6 7 9 11 15 86 1848 1848', '4 2 +4 +4']},
          'Max INT': {'func': cmd_error,
                      'test': ['1 2147483648 8 4 2 3', '1 6 8 2147483649 2 3', '1 6 -2147483649 4 2 3', '-2147483649 1 6 8 4 2 3']},
          'Nothing to return': {'func': cmd_nothing_return,
                                'test': ['', '42', '30', '-5', '0 1 2 3', '-185 26 48 8546', '0 1 2 3 +4 5 6 7 +8 9 10 11', '-554949 -2549 -695 15 45948 545498', '548 9898', '1 2']},
          'Parsing': {'func': cmd_parsing,
                      'test': ['5 +4 -659', '+8498 70 -4659', '"0 5 8 9"', '"0 5 1 9 2"', '"5 6 8 9"', '"9 5 8 -1288"', '"0 5 9" 8', '"    +2 5 9" 8', '"    -2 5 9" 8', '0 5 1 "9 2"', '"5" 6 8 9', '"9 5" 8 -1288', '""""']}
          }

if 'evaluating' in sys.argv:
    print_color("\n→ Error management:", C.BLUE, False)

    for title, val in checks.items():
        print_color(f"\n  {title}", C.PINK)

        for test in val['test']:
            val['func'](test)

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
    for val in checks.values():
        for test in val['test']:
            cmd_leaks(test)

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
