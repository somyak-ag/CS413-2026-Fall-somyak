Assignment 2 — Pairs/Projections and an ATS-to-LAMBDA0 Translation

Files:

- `lambda0.py` — the starter interpreter with support for `T0Mpair`, `T0Mpfst`, and `T0Mpsnd`.
- `TEST/test02_lambda0.py` — tests for the pairs and projections.
- `queens.dats` — the original ATS2 eight-queens program.
- `queens_lambda0.py` — the LAMBDA0 version of the queens program.
- `TEST/test03_queens.py` — tests for the queens translation.

Running the tests:

I used the same `unittest` style as the provided tests.


python3 MySolution/TEST/test01_lambda0.py
python3 MySolution/TEST/test02_lambda0.py
python3 MySolution/TEST/test03_queens.py
SKIP_SLOW_QUEENS_TESTS=1 python3 MySolution/TEST/test03_queens.py


The first test is the original test file provided with the assignment. The second tests the pairs and projections, and the third tests the queens translation.

All three can also be run together with:


python3 -m unittest discover -s MySolution/TEST -v


or with `pytest`.

`test01_lambda0.py` passes all 27 tests after adding the new pair and projection functionality.

The queens tests for smaller values of N run fairly quickly. N=7 takes around 30–40 seconds, while N=8 takes much longer and uses a lot more memory, so there is an option to skip that test.

Running the queens program:

The queens program can also be run directly:


python3 MySolution/queens_lambda0.py
python3 MySolution/queens_lambda0.py 6


The first command runs the original N=8 case, while the second runs it for N=6.

Part 1–3: Pairs and projections:

I added `T0Mpair`, `T0Mpfst`, and `T0Mpsnd` to the different functions in `lambda0.py`.

For `t0erm_size`, I treated a pair or projection as one node plus the size of its contents.

For `t0erm_fvset`, I collected the free variables from both sides of a pair, or from the expression inside a projection. Pairs and projections do not introduce any new variables.

For `t0erm_subst0`, substitution just continues recursively into the pair or projection. There is no special shadowing case because these constructs do not bind variables.

For `t0erm_cbv_evaluate0`, both parts of a pair are evaluated from left to right. A pair is only a value after both parts have been evaluated. A projection first evaluates its argument and then checks that it is actually a pair.

I tested these cases in `test02_lambda0.py`, including nested pairs, projections, substitution, functions that take or return pairs, and some cases involving recursion.

I also tested the division-by-zero examples from the assignment to make sure the evaluation order was correct. For example:


T0Mpfst(T0Mpair(T0Mint(1), 1/0))


still evaluates the second part of the pair, so it raises the expected `ZeroDivisionError`.

I did not need to add any new primitive operations because the starter interpreter already had the comparison operations needed for the queens program.

Part 4: Translating the ATS eight-queens program:

Source:

The original `queens.dats` comes from Section 3.9 of Hongwei Xi's Introduction to Programming in ATS.

The program represents the board as a tuple of integers. It has functions for getting and setting board positions, checking whether a queen placement is safe, and recursively searching for all solutions.

I translated this into LAMBDA0 while keeping the same basic structure of the original program.

Representation choices:

Board:

Since LAMBDA0 does not have arrays, I represented the board using nested pairs.

For example, a board can look like:

pair(x0, pair(x1, pair(x2, ...)))


This lets me use `fst` and `snd` to access the different values.

`board_get` and `board_set` are built using if-statements based on the row number. This is similar to what the original ATS program does because the original also does not use arrays.

Functions with multiple arguments:

LAMBDA0 functions only take one argument at a time, so functions with multiple arguments from the ATS program have to be curried.

For example:


fun f(a, b, c) = ...


becomes a chain like:

fix f = lam a => lam b => lam c => ...


The function is then applied one argument at a time.

Let expressions:

LAMBDA0 does not have its own `let` expression, so I represented:


let x = e1 in e2


as:


(lam x => e2)(e1)


This also matches how a one-variable `let` can be represented using a lambda application.

Recursion and free variables:

The functions in the queens program are defined using a chain of `let` expressions. This lets the earlier definitions get substituted into the functions that come later.

For example, `search` uses the other functions, and it also refers to itself using `T0Mfix`.

I also checked that the final queens term has no free variables. This is tested in `test03_queens.py`.

Printing and I/O:

One difference between the ATS program and the LAMBDA0 version is that LAMBDA0 does not have normal printing or other side effects.

The ATS program prints every solution and keeps track of the number of solutions. Instead of printing them inside LAMBDA0, I returned the information as a pair:


(count, solutions)


The `solutions` part is represented as a list using pairs.

This lets the Python code outside of the LAMBDA0 evaluator look at the results after the program finishes.

The actual search and safety-checking logic stays the same as the ATS version.

Running and checking the results:

Running:

python3 queens_lambda0.py 6


builds the LAMBDA0 term and evaluates it. The Python code then takes the returned count and list of solutions and checks the boards.

I compared the results with the known number of solutions for the N-queens problem.

| N | Expected count | LAMBDA0 count |
|---|---:|---:|
| 1 | 1 | 1 |
| 2 | 0 | 0 |
| 3 | 0 | 0 |
| 4 | 2 | 2 |
| 5 | 10 | 10 |
| 6 | 4 | 4 |
| 7 | 40 | 40 |
| 8 | 92 | 92 |

I also checked the returned boards for N=1 through N=7 to make sure there were no row, column, or diagonal conflicts.

The N=8 version was also run separately and returned 92 solutions.

Limitations:

The main issue I found was performance for N=8.

The original ATS search is tail-recursive, but the Python evaluator used by LAMBDA0 does not have tail-call optimization. Because of this, even calls that are tail calls in the original program still create more Python stack frames.

The substitution-based evaluator also copies a lot of the program while it runs. This makes the larger N=8 case very slow and memory-intensive.

N=1 through N=7 work correctly and match the expected solution counts. N=8 also gives the correct answer, 92, but it takes much longer and uses a lot of memory, so I made the N=8 test skippable.

Another difference is the printing. Since LAMBDA0 does not have I/O, I changed the printing part of the ATS program into returning the solutions as part of the result. The actual search logic and safety checks were kept the same.

Note on AI Use:

I used AI while working on this assignment, but mainly as a tool to help me edit and debug my code.

I first drafted the code myself and then used AI to help make edits, fix errors, and work through parts that were not working. After making changes, I tested the code myself and went back and fixed anything that failed.

For the pairs and projections, I tested the different cases from the assignment and also ran the original tests again to make sure I did not break anything that was already working.

For the queens translation, I ran the program for different values of N and checked the number of solutions and the returned boards. This also helped me find the performance and memory problem with N=8.

I also went through the code myself to understand how the substitution and evaluation were working, especially with pairs, projections, recursion, and the translation from ATS to LAMBDA0.

So, AI was mainly used to help with editing and debugging my draft. I still tested the changes myself and made sure I understood and verified the final code.
