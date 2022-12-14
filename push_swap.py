import os
import sys
import random
import subprocess

int_min = -2147483648
int_max = 2147483647
makefile_cmd = 'make'
checker_path = 'checker_Mac'
if not os.path.exists(checker_path):
    checker_path = 'push_Swap-tester/' + checker_path
push_swap_path = f'{os.path.split(os.path.dirname(__file__))[0]}/push_swap'
os.popen(makefile_cmd).read()
eval_pts = {100: {'pts': {700: 5, 900: 4, 1100: 3, 1300: 2, 1500: 1}, 'max': -1}, 500: {'pts': {5500: 5, 7000: 4, 8500: 3, 10000: 2, 11500: 1}, 'max': -1}}


# General --------------------------------------------------------
def get_random_number(k):
    return ' '.join([str(nb) for nb in random.sample(range(int_min, int_max), k=k)])


# ERROR ----------------------------------------------------------
def error(string_):
    print('Error: ' + string_)


def cmd_error(args):
    res = cmd(args, True)
    if res != "Error\n":
        error(f"With '{args}' we must have \"Error\", we have '{res}'")
    else:
        print("\tOK")


def cmd_nothing_return(args):
    if cmd(args):
        error(f"Your program should return nothing, he return '{args}'")
    else:
        print("\tOK")


def cmd_parsing(args):
    if cmd(args) == "Error\n":
        error(f"Parsing error with '{args}'")
    else:
        print("\tOK")


def cmd_leaks(args):
    if os.system(f'leaks -atExit -- {push_swap_path} {args}') > 0:
        print(f'Leaks Error ! With \'{args}\'')
        exit()


# CMD ------------------------------------------------------------
def cmd(args, stderror=False):
    proc = subprocess.Popen([push_swap_path, args], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return proc.stderr.read().decode() if stderror else proc.stdout.read().decode()


def cmd_check(args):
    return os.popen(f'{push_swap_path} {args} | ./{checker_path} {args}').read().removesuffix('\n')


def cmd_count(args):
    return len(cmd(args).split('\n')) - 1


def cmd_all_n(n, evaluating=False):
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

    for comb in all_comb:
        check = cmd_check(comb)
        if check == "KO":
            error(f"\tKO don't sort '{comb}'")
        ct = len(cmd(comb).split('\n')) - 1
        all_count.append(ct)
        if n == 5 and ct > 12:
            error(f"\tKO you sort in more than 12 instructions '{comb}'")
        elif n == 3 and ct > 3:
            error(f"\tKO you sort in more than 3 instructions '{comb}'")
        elif not evaluating or n == 3 or all_comb.index(comb) % 20 == 0:
            print("\tOK" + (f' - {"" if ct >= 10 else " "}{ct}  |  {comb}', '')[evaluating])
    return all_count


def cmd_middle(n):
    args = get_random_number(n)
    check = cmd_check(args)
    if check == "KO":
        error(f"\tKO: don't sort '{args}'")
    else:
        ct = cmd_count(args)
        pt = 0
        for max_ins in eval_pts[n]['pts']:
            if ct < max_ins:
                pt = eval_pts[n]['pts'][max_ins]

                break
        if eval_pts[n]['max'] < pt:
            eval_pts[n]['max'] = pt
            print(f"\tOK sort in {ct} - {pt} pts")
            if '-a' in sys.argv:
                print(f'ARGS = {args}')


# CODE ---------------------------------------------------------------

if not os.path.exists(push_swap_path) or not os.path.exists(checker_path):
    print(f'Error: don\'t find {push_swap_path} or {checker_path}')
    exit()

if 'evaluating' in sys.argv:
    print("Error management:")

    print("  Non numeric")
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

    print("\n  Duplicate args")
    cmd_error("2 6 3 6")
    cmd_error("6 6 3")
    cmd_error("3 6 3")
    cmd_error("1 6 8 4 2 3 1")

    print("\n  Max INT")
    cmd_error("1 2147483648 8 4 2 3")
    cmd_error("1 6 8 2147483649 2 3")
    cmd_error("1 6 -2147483649 4 2 3")
    cmd_error("-2147483649 1 6 8 4 2 3")

    print("\n  Nothing to return")
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

    print("\n  Parsing")
    cmd_error('""')
    cmd_parsing('"0 5 8 9"')
    cmd_parsing('"0 5 1 9 2"')
    cmd_parsing('"5 6 8 9"')
    cmd_parsing('"9 5 8 -1288"')

    cmd_parsing('"0 5 9" 8')
    cmd_parsing('0 5 1 "9 2"')
    cmd_parsing('"5" 6 8 9')
    cmd_parsing('"9 5" 8 -1288')

    print("\nSimple version:")

    print("  3 args")
    cmd_all_n(3, True)
    print("\n  5 args")
    cmd_all_n(5, True)

    print("\nMiddle version:")

    print("  100 random")
    for _ in range(100):
        cmd_middle(100)

    print("\n  500 random")
    for _ in range(50):
        cmd_middle(500)
elif 'leaks' in sys.argv:

    print("Leaks Error\n")
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

elif 'all' in sys.argv:
    all_ct = cmd_all_n(int(sys.argv[2]) if len(sys.argv) == 3 and sys.argv[2].isdigit() else 5)
    print(f'mean = {int(sum(all_ct) / len(all_ct))} - max_len = {max(all_ct)}')

else:
    length_args = int(sys.argv[1]) if len(sys.argv) >= 2 and sys.argv[1].isdigit() else 100
    n_time = int(sys.argv[2]) if len(sys.argv) >= 3 and sys.argv[2].isdigit() else 1
    if length_args in eval_pts:
        for _ in range(n_time):
            eval_pts[length_args]['max'] = -1
            cmd_middle(length_args)
    else:
        for _ in range(n_time):
            args_check = get_random_number(length_args)
            print(f'{cmd_check(args_check)} - len {len(args_check.split(" "))} in {cmd_count(args_check)} commands')
            if '-a' in sys.argv:
                print(f'ARGS = {args_check}')
