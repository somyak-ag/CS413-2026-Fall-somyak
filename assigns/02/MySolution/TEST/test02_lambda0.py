"""Examples for the pairs/projections extension to lambda0.py.

Run with: python3 TEST/test02_lambda0.py
Requires Python 3.12 or later, like lambda0.py.
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lambda0 import (
    T0Mint, T0Mbtf, T0Mstr, T0Mvar, T0Mlam, T0Mfix, T0Mapp, T0Mif0, T0Mop1, T0Mop2,
    T0Mpair, T0Mpfst, T0Mpsnd,
    t0erm_size, t0erm_fvset, t0erm_subst0, t0erm_cbv_evaluate0,
)


class TestSize(unittest.TestCase):
    def test_pair(self):
        self.assertEqual(t0erm_size(T0Mpair(T0Mint(1), T0Mint(2))), 3)

    def test_projections(self):
        p = T0Mpair(T0Mint(1), T0Mint(2))
        self.assertEqual(t0erm_size(T0Mpfst(p)), 1 + t0erm_size(p))
        self.assertEqual(t0erm_size(T0Mpsnd(p)), 1 + t0erm_size(p))
        self.assertEqual(t0erm_size(T0Mpfst(p)), 4)
        self.assertEqual(t0erm_size(T0Mpsnd(p)), 4)

    def test_nested_pairs(self):
        inner_right = T0Mpair(T0Mint(4), T0Mint(5))
        right = T0Mpair(T0Mint(3), inner_right)
        left = T0Mpair(T0Mint(1), T0Mint(2))
        whole = T0Mpair(left, right)
        self.assertEqual(t0erm_size(whole), 9)

    def test_pair_inside_other_constructs(self):
        term = T0Mif0(
            T0Mbtf(True),
            T0Mpair(T0Mint(1), T0Mint(2)),
            T0Mpair(T0Mint(3), T0Mint(4)),
        )
        self.assertEqual(t0erm_size(term), 1 + 1 + 3 + 3)


class TestFvset(unittest.TestCase):
    def test_pfst_pair_of_vars(self):
        self.assertEqual(
            t0erm_fvset(T0Mpfst(T0Mpair(T0Mvar("x"), T0Mvar("y")))),
            frozenset({"x", "y"}),
        )

    def test_psnd_pair_of_vars(self):
        self.assertEqual(
            t0erm_fvset(T0Mpsnd(T0Mpair(T0Mvar("x"), T0Mvar("y")))),
            frozenset({"x", "y"}),
        )

    def test_pair_binds_no_variable(self):
        term = T0Mlam("x", T0Mpair(T0Mvar("x"), T0Mvar("y")))
        self.assertEqual(t0erm_fvset(term), frozenset({"y"}))

    def test_nested_pair_and_projection(self):
        term = T0Mpfst(T0Mpair(T0Mpsnd(T0Mpair(T0Mvar("a"), T0Mvar("b"))), T0Mvar("c")))
        self.assertEqual(t0erm_fvset(term), frozenset({"a", "b", "c"}))


class TestSubst(unittest.TestCase):
    def test_into_pair_components(self):
        term = T0Mpair(T0Mvar("x"), T0Mvar("y"))
        result = t0erm_subst0(term, "x", T0Mint(42))
        self.assertEqual(result, T0Mpair(T0Mint(42), T0Mvar("y")))

    def test_into_projection_operand(self):
        term = T0Mpfst(T0Mpair(T0Mvar("x"), T0Mvar("x")))
        result = t0erm_subst0(term, "x", T0Mint(7))
        self.assertEqual(result, T0Mpfst(T0Mpair(T0Mint(7), T0Mint(7))))

    def test_under_lambda_binder(self):
        term = T0Mlam("x", T0Mpair(T0Mvar("x"), T0Mvar("y")))
        result = t0erm_subst0(term, "y", T0Mint(9))
        self.assertEqual(result, T0Mlam("x", T0Mpair(T0Mvar("x"), T0Mint(9))))
        self.assertEqual(t0erm_subst0(term, "x", T0Mint(9)), term)

    def test_under_fix_binder(self):
        body = T0Mpair(T0Mvar("x"), T0Mapp(T0Mvar("f"), T0Mvar("y")))
        term = T0Mfix("f", "x", body)
        self.assertEqual(t0erm_subst0(term, "f", T0Mint(0)), term)
        result = t0erm_subst0(term, "y", T0Mint(3))
        expected = T0Mfix("f", "x", T0Mpair(T0Mvar("x"), T0Mapp(T0Mvar("f"), T0Mint(3))))
        self.assertEqual(result, expected)


class TestCBVEvaluatePairs(unittest.TestCase):
    def test_pair_of_values(self):
        result = t0erm_cbv_evaluate0(T0Mpair(T0Mint(1), T0Mint(2)))
        self.assertEqual(result, T0Mpair(T0Mint(1), T0Mint(2)))

    def test_pair_with_components_needing_evaluation(self):
        term = T0Mpair(T0Mop2("+", T0Mint(1), T0Mint(2)), T0Mop2("*", T0Mint(3), T0Mint(4)))
        self.assertEqual(t0erm_cbv_evaluate0(term), T0Mpair(T0Mint(3), T0Mint(12)))

    def test_pfst_and_psnd_of_evaluated_pair(self):
        term = T0Mpair(T0Mop2("+", T0Mint(1), T0Mint(2)), T0Mop2("*", T0Mint(3), T0Mint(4)))
        self.assertEqual(t0erm_cbv_evaluate0(T0Mpfst(term)), T0Mint(3))
        self.assertEqual(t0erm_cbv_evaluate0(T0Mpsnd(term)), T0Mint(12))

    def test_psnd_example_from_spec(self):
        term = T0Mpsnd(T0Mpair(T0Mint(1), T0Mop2("+", T0Mint(2), T0Mint(3))))
        self.assertEqual(t0erm_cbv_evaluate0(term), T0Mint(5))

    def test_nested_pairs(self):
        term = T0Mpair(T0Mpair(T0Mint(1), T0Mint(2)), T0Mpair(T0Mint(3), T0Mint(4)))
        result = t0erm_cbv_evaluate0(term)
        self.assertEqual(result, term)
        self.assertEqual(t0erm_cbv_evaluate0(T0Mpfst(T0Mpfst(term))), T0Mint(1))
        self.assertEqual(t0erm_cbv_evaluate0(T0Mpsnd(T0Mpsnd(term))), T0Mint(4))

    def test_pair_of_mixed_kinds(self):
        f = T0Mlam("z", T0Mop2("+", T0Mvar("z"), T0Mint(1)))
        term = T0Mpair(T0Mint(10), f)
        self.assertEqual(t0erm_cbv_evaluate0(term), T0Mpair(T0Mint(10), f))
        call = T0Mapp(T0Mpsnd(term), T0Mint(41))
        self.assertEqual(t0erm_cbv_evaluate0(call), T0Mint(42))

    def test_pair_containing_pair_and_function(self):
        inner = T0Mpair(T0Mint(1), T0Mint(2))
        f = T0Mlam("p", T0Mop2("+", T0Mpfst(T0Mvar("p")), T0Mpsnd(T0Mvar("p"))))
        term = T0Mpair(inner, f)
        call = T0Mapp(T0Mpsnd(term), T0Mpfst(term))
        self.assertEqual(t0erm_cbv_evaluate0(call), T0Mint(3))

    def test_function_accepting_pair(self):
        f = T0Mlam("p", T0Mop2("+", T0Mpfst(T0Mvar("p")), T0Mpsnd(T0Mvar("p"))))
        term = T0Mapp(f, T0Mpair(T0Mint(3), T0Mint(4)))
        self.assertEqual(t0erm_cbv_evaluate0(term), T0Mint(7))

    def test_function_returning_pair(self):
        f = T0Mlam("x", T0Mpair(T0Mvar("x"), T0Mop2("+", T0Mvar("x"), T0Mint(1))))
        term = T0Mapp(f, T0Mint(5))
        self.assertEqual(t0erm_cbv_evaluate0(term), T0Mpair(T0Mint(5), T0Mint(6)))

    def test_recursive_function_over_pair_list(self):
        body = T0Mif0(
            T0Mop2("==", T0Mpfst(T0Mvar("p")), T0Mint(0)),
            T0Mint(0),
            T0Mop2("+", T0Mpfst(T0Mvar("p")),
                   T0Mapp(T0Mvar("sumlist"), T0Mpsnd(T0Mvar("p")))),
        )
        sumlist = T0Mfix("sumlist", "p", body)
        lst = T0Mpair(T0Mint(3),
                      T0Mpair(T0Mint(2),
                              T0Mpair(T0Mint(1), T0Mpair(T0Mint(0), T0Mint(0)))))
        term = T0Mapp(sumlist, lst)
        self.assertEqual(t0erm_cbv_evaluate0(term), T0Mint(6))

    def test_projection_on_non_pair_raises(self):
        for term in (T0Mpfst(T0Mint(5)), T0Mpsnd(T0Mbtf(True)), T0Mpfst(T0Mlam("x", T0Mvar("x")))):
            with self.subTest(term=term):
                with self.assertRaises(TypeError):
                    t0erm_cbv_evaluate0(term)

    def test_pfst_still_evaluates_snd_component(self):
        term = T0Mpfst(T0Mpair(T0Mint(1), T0Mop2("/", T0Mint(1), T0Mint(0))))
        with self.assertRaises(ZeroDivisionError):
            t0erm_cbv_evaluate0(term)

    def test_psnd_still_evaluates_fst_component(self):
        term = T0Mpsnd(T0Mpair(T0Mop2("/", T0Mint(1), T0Mint(0)), T0Mint(2)))
        with self.assertRaises(ZeroDivisionError):
            t0erm_cbv_evaluate0(term)

    def test_left_to_right_evaluation_order(self):
        left_bad = T0Mop2("/", T0Mint(1), T0Mint(0))
        right_bad = T0Mop2("%", T0Mint(1), T0Mstr("x"))
        term = T0Mpair(left_bad, right_bad)
        with self.assertRaises(ZeroDivisionError):
            t0erm_cbv_evaluate0(term)


if __name__ == "__main__":
    unittest.main(verbosity=2)
