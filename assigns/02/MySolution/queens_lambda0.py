import os
import sys
import threading

sys.path.insert(0, os.path.dirname(__file__))

sys.setrecursionlimit(1_000_000)

from lambda0 import (
    T0Mvar, T0Mlam, T0Mfix, T0Mapp, T0Mint, T0Mbtf, T0Mstr,
    T0Mop1, T0Mop2, T0Mif0, T0Mpair, T0Mpfst, T0Mpsnd,
    t0erm_cbv_evaluate0,
)


def V(x):
    return T0Mvar(x)

def I(n):
    return T0Mint(n)

def op2(op, a, b):
    return T0Mop2(op, a, b)

def op1(op, a):
    return T0Mop1(op, a)

def iff(c, t, e):
    return T0Mif0(c, t, e)

def lam(x, body):
    return T0Mlam(x, body)

def app(f, a):
    return T0Mapp(f, a)

def appn(f, *args):
    for a in args:
        f = T0Mapp(f, a)
    return f

def pair(a, b):
    return T0Mpair(a, b)

def fst(t):
    return T0Mpfst(t)

def snd(t):
    return T0Mpsnd(t)

def let_(name, val, body):
    return T0Mapp(T0Mlam(name, body), val)


def board_literal(xs):
    xs = list(xs)
    e = I(xs[-1])
    for x in reversed(xs[:-1]):
        e = pair(I(x), e)
    return e

def accessor(bd_expr, k, n):
    e = bd_expr
    for _ in range(k):
        e = snd(e)
    if k < n - 1:
        e = fst(e)
    return e

def rebuild(n, comps):
    e = comps[-1]
    for c in reversed(comps[:-1]):
        e = pair(c, e)
    return e


def build_board_get(n):
    bd, i = "bd", "i"
    body = accessor(V(bd), n - 1, n)
    for k in range(n - 2, -1, -1):
        body = iff(op2("==", V(i), I(k)), accessor(V(bd), k, n), body)
    return lam(bd, lam(i, body))


def build_board_set(n):
    bd, i, j = "bd", "i", "j"
    xs = [f"x{k}" for k in range(n)]

    def comps_with(replaced_k):
        return [V(j) if k == replaced_k else V(xs[k]) for k in range(n)]

    chain = V(bd)
    for k in range(n - 1, -1, -1):
        chain = iff(op2("==", V(i), I(k)), rebuild(n, comps_with(k)), chain)

    body = chain
    for k in reversed(range(n)):
        body = let_(xs[k], accessor(V(bd), k, n), body)

    return lam(bd, lam(i, lam(j, body)))


def build_safety_test1():
    i0, j0, i1, j1 = "i0", "j0", "i1", "j1"
    abs_lam = lam("x", iff(op2("<", V("x"), I(0)), op1("-", V("x")), V("x")))

    def andalso(a, b):
        return iff(a, b, T0Mbtf(False))

    body = andalso(
        op2("!=", V(j0), V(j1)),
        op2("!=",
            app(V("abs"), op2("-", V(i0), V(i1))),
            app(V("abs"), op2("-", V(j0), V(j1)))),
    )
    func = lam(i0, lam(j0, lam(i1, lam(j1, body))))
    return let_("abs", abs_lam, func)


def build_safety_test2():
    i0, j0, bd, i = "i0", "j0", "bd", "i"
    body = iff(
        op2(">=", V(i), I(0)),
        iff(
            appn(V("safety_test1"), V(i0), V(j0), V(i), appn(V("board_get"), V(bd), V(i))),
            appn(V("safety_test2"), V(i0), V(j0), V(bd), op2("-", V(i), I(1))),
            T0Mbtf(False),
        ),
        T0Mbtf(True),
    )
    return T0Mfix("safety_test2", i0, lam(j0, lam(bd, lam(i, body))))


def build_search(n):
    bd, i, j, state = "bd", "i", "j", "state"
    body = iff(
        op2("<", V(j), I(n)),
        let_("test", appn(V("safety_test2"), V(i), V(j), V(bd), op2("-", V(i), I(1))),
             iff(
                 V("test"),
                 let_("bd1", appn(V("board_set"), V(bd), V(i), V(j)),
                      iff(
                          op2("==", op2("+", V(i), I(1)), I(n)),
                          let_("state1",
                               pair(op2("+", fst(V(state)), I(1)),
                                    pair(V("bd1"), snd(V(state)))),
                               appn(V("search"), V(bd), V(i), op2("+", V(j), I(1)), V("state1"))),
                          appn(V("search"), V("bd1"), op2("+", V(i), I(1)), I(0), V(state)),
                      )),
                 appn(V("search"), V(bd), V(i), op2("+", V(j), I(1)), V(state)),
             )),
        iff(
            op2(">", V(i), I(0)),
            appn(V("search"), V(bd), op2("-", V(i), I(1)),
                 op2("+", appn(V("board_get"), V(bd), op2("-", V(i), I(1))), I(1)), V(state)),
            V(state),
        ),
    )
    return T0Mfix("search", bd, lam(i, lam(j, lam(state, body))))


def build_queens_term(n):
    board0 = board_literal([0] * n)
    state0 = pair(I(0), T0Mbtf(False))
    main = appn(V("search"), board0, I(0), I(0), state0)

    return let_("board_get", build_board_get(n),
           let_("board_set", build_board_set(n),
           let_("safety_test1", build_safety_test1(),
           let_("safety_test2", build_safety_test2(),
           let_("search", build_search(n),
                main)))))


def board_to_tuple(term, n):
    xs = []
    t = term
    for k in range(n - 1):
        xs.append(t.arg1.arg1)
        t = t.arg2
    xs.append(t.arg1)
    return tuple(xs)

def solutions_to_list(term, n):
    out = []
    t = term
    while isinstance(t, T0Mpair):
        out.append(board_to_tuple(t.arg1, n))
        t = t.arg2
    return out

def print_board(bd):
    n = len(bd)
    for i in range(n):
        row = ". " * bd[i] + "Q " + ". " * (n - bd[i] - 1)
        print(row)
    print()

def is_valid_solution(bd):
    n = len(bd)
    if len(set(bd)) != n:
        return False
    for i in range(n):
        for k in range(i + 1, n):
            if abs(bd[i] - bd[k]) == k - i:
                return False
    return True

def run_queens(n):
    term = build_queens_term(n)
    result = t0erm_cbv_evaluate0(term)
    count = result.arg1.arg1
    solutions = solutions_to_list(result.arg2, n)
    return count, solutions

def run_queens_on_thread(n, stack_size=512 * 1024 * 1024):
    result_box = {}

    def target():
        result_box["value"] = run_queens(n)

    old_stack_size = threading.stack_size()
    threading.stack_size(stack_size)
    t = threading.Thread(target=target)
    t.start()
    t.join()
    threading.stack_size(old_stack_size)
    return result_box["value"]


if __name__ == "__main__":
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 8

    print(f"Running the translated LAMBDA0 program for N={N}...")
    count, solutions = run_queens_on_thread(N)

    print(f"There are {count} distinct solutions in total.\n")
    if solutions:
        print("Solution #1:\n")
        print_board(solutions[-1])

    bad = [s for s in solutions if not is_valid_solution(s)]
    print(f"Solutions recorded: {len(solutions)}; invalid among them: {len(bad)}")
