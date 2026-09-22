"""Examples for the eight-queens LAMBDA0 translation in queens_lambda0.py.

Run with: python3 TEST/test03_queens.py
Requires Python 3.12 or later, like lambda0.py.
"""

import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lambda0 import T0Mint, T0Mfix, T0Mvar, t0erm_fvset, t0erm_cbv_evaluate0
from queens_lambda0 import (
    build_queens_term, build_board_get, build_board_set,
    build_safety_test1, build_safety_test2, let_,
    run_queens, run_queens_on_thread,
    board_literal, board_to_tuple,
    is_valid_solution, appn, V, I,
)

SKIP_SLOW = os.environ.get("SKIP_SLOW_QUEENS_TESTS") == "1"

KNOWN_SOLUTION_COUNTS = {1: 1, 2: 0, 3: 0, 4: 2, 5: 10, 6: 4, 7: 40, 8: 92}


class TestBoardGetSet(unittest.TestCase):
    def test_board_get_reads_every_position(self):
        n = 5
        bg = build_board_get(n)
        board = board_literal([3, 0, 4, 1, 2])
        for i, expected in enumerate([3, 0, 4, 1, 2]):
            with self.subTest(i=i):
                term = appn(bg, board, I(i))
                self.assertEqual(t0erm_cbv_evaluate0(term), T0Mint(expected))

    def test_board_set_replaces_one_position_only(self):
        n = 5
        bs = build_board_set(n)
        board = board_literal([3, 0, 4, 1, 2])
        term = appn(bs, board, I(2), I(9))
        result = t0erm_cbv_evaluate0(term)
        self.assertEqual(board_to_tuple(result, n), (3, 0, 9, 1, 2))

    def test_board_set_then_get_roundtrip(self):
        n = 4
        bg, bs = build_board_get(n), build_board_set(n)
        board = board_literal([0, 0, 0, 0])
        for i in range(n):
            board = t0erm_cbv_evaluate0(appn(bs, board, I(i), I(i + 1)))
        self.assertEqual(board_to_tuple(board, n), (1, 2, 3, 4))
        for i in range(n):
            with self.subTest(i=i):
                self.assertEqual(t0erm_cbv_evaluate0(appn(bg, board, I(i))), T0Mint(i + 1))


class TestSafetyChecks(unittest.TestCase):
    def test_same_column_is_unsafe(self):
        st1 = t0erm_cbv_evaluate0(build_safety_test1())
        term = appn(st1, I(0), I(2), I(1), I(2))
        self.assertFalse(t0erm_cbv_evaluate0(term).arg1)

    def test_same_diagonal_is_unsafe(self):
        st1 = t0erm_cbv_evaluate0(build_safety_test1())
        term = appn(st1, I(0), I(0), I(2), I(2))
        self.assertFalse(t0erm_cbv_evaluate0(term).arg1)

    def test_safe_position(self):
        st1 = t0erm_cbv_evaluate0(build_safety_test1())
        term = appn(st1, I(0), I(0), I(1), I(2))
        self.assertTrue(t0erm_cbv_evaluate0(term).arg1)

    def test_safety_test2_detects_conflict_against_board(self):
        n = 4
        board = board_literal([0, 2, 0, 0])
        prog = let_("board_get", build_board_get(n),
               let_("safety_test1", build_safety_test1(),
               let_("safety_test2", build_safety_test2(),
                    let_("bd", board,
                         appn(V("safety_test2"), I(2), I(2), V("bd"), I(1))))))
        self.assertFalse(t0erm_cbv_evaluate0(prog).arg1)


class TestSolutionCounts(unittest.TestCase):
    def test_small_boards(self):
        for n in (4, 5, 6):
            with self.subTest(n=n):
                count, solutions = run_queens(n)
                self.assertEqual(count, KNOWN_SOLUTION_COUNTS[n])
                self.assertEqual(len(solutions), KNOWN_SOLUTION_COUNTS[n])

    def test_n1(self):
        count, solutions = run_queens(1)
        self.assertEqual(count, 1)
        self.assertEqual(solutions, [(0,)])

    def test_no_solutions_for_n2_and_n3(self):
        for n in (2, 3):
            with self.subTest(n=n):
                count, solutions = run_queens(n)
                self.assertEqual(count, 0)
                self.assertEqual(solutions, [])


class TestBoardValidity(unittest.TestCase):
    def test_every_recorded_board_has_no_conflicts(self):
        for n in (4, 5, 6):
            _, solutions = run_queens(n)
            for board in solutions:
                with self.subTest(n=n, board=board):
                    self.assertEqual(len(board), n)
                    self.assertTrue(is_valid_solution(board))

    def test_all_n4_solutions_are_the_two_known_ones(self):
        _, solutions = run_queens(4)
        self.assertEqual(set(solutions), {(1, 3, 0, 2), (2, 0, 3, 1)})

    def test_is_valid_solution_rejects_same_column(self):
        self.assertFalse(is_valid_solution((0, 0, 2, 3)))

    def test_is_valid_solution_rejects_same_diagonal(self):
        self.assertFalse(is_valid_solution((0, 1, 2, 3)))

    def test_is_valid_solution_accepts_known_solution(self):
        self.assertTrue(is_valid_solution((1, 3, 0, 2)))


class TestClosedTerm(unittest.TestCase):
    def test_queens_term_has_no_free_variables(self):
        term = build_queens_term(4)
        self.assertEqual(t0erm_fvset(term), frozenset())


class TestFullBoard(unittest.TestCase):
    @unittest.skipIf(SKIP_SLOW, "SKIP_SLOW_QUEENS_TESTS=1 set")
    def test_n8_matches_ats_original(self):
        count, solutions = run_queens_on_thread(8)
        self.assertEqual(count, 92)
        self.assertEqual(len(solutions), 92)
        for board in solutions:
            self.assertTrue(is_valid_solution(board))


if __name__ == "__main__":
    unittest.main(verbosity=2)
