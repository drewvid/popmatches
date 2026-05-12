import unittest
import builtins
from collections import OrderedDict
from popmatches import (
    smatches, matches, disable_globals, enable_globals, 
    clear_globals, var_one, var_many, V, mexp, match_procedure
)

class TestMatchesLegacy(unittest.TestCase):
    """Modernized version of the original test_matches.py."""

    def setUp(self):
        clear_globals()
        enable_globals()
        V.clear()

    def test_smatches_patterns(self):
        """Test various smatches patterns (strings)."""
        # (text, pattern, expected_success)
        # Note: If expected_success is a dict, we verify bindings.
        test_cases = [
            ('1 2 3 4', '==', True),
            ('1', '== 1 ==', True),
            ('1 2', '== 2 ==', True),
            ('2 3', '== 2 ==', True),
            ('1 2 3', '== 2 ==', True),
            ('1', '=', True),
            ('1 2 3', '= 2 =', True),
            
            ('1 2 3 4', '?X 2 ??Y', {'X': '1', 'Y': ['3', '4']}),
            ('1 2 3 4', '??X:1 2 ??Y', {'X': ['1'], 'Y': ['3', '4']}),
            ('1 2 3 4', '??X:2 3 ?Y', {'X': ['1', '2'], 'Y': '4'}),
            ('1 2 3 4 5', '??X 3 ??Y', {'X': ['1', '2'], 'Y': ['4', '5']}),
            ('3', '??X 3 ??Y', {'X': [], 'Y': []}),
            ('3', '== 3 ??Y', {'Y': []}),
            ('2 3', '??X 3 ??Y', {'X': ['2'], 'Y': []}),
            ('3 4', '??X 3 ??Y', {'X': [], 'Y': ['4']}),
            ('1 2 3', '?X 2 ?Y', {'X': '1', 'Y': '3'}),
            ('1 2 3', '??X:1 2 ??Y:1', {'X': ['1'], 'Y': ['3']}),
            
            ('3', '?X 3 ?Y', False),
            ('2 3', '?X 3 ?Y', False),
            ('3 4', '?X 3 ?Y', False),
            ('1', '= 1 =', False),
            ('1 2 3', '= 2', False),
            ('1 2 3', '2 =', False),
        ]

        for text, pattern, expected in test_cases:
            with self.subTest(text=text, pattern=pattern):
                res = smatches(text, pattern)
                if expected is True:
                    self.assertTrue(res)
                elif expected is False:
                    self.assertFalse(res)
                else:
                    self.assertEqual(res, OrderedDict(expected))

    def test_complex_matches(self):
        """Test complex nested list matches and procedural matches."""
        @match_procedure
        def zero(x): return 'zero' if x == 0 else False
        @match_procedure
        def five(x): return 'five' if x == 5 else False

        v1p_ = var_one(proc=zero)
        v2_ = var_one()
        v3_ = var_one(vname='v3')
        v4p_ = var_one(vname='v4', proc=five)
        v5_ = var_one(vname='v5')

        data = [0, 1, 2, 3, 4, 5, [['a', 'b'], 'c']]
        pattern = [v1p_, v2_, 2, v3_, 4, v4p_, [['a', 'b'], v5_]]
        res = matches(data, pattern)
        self.assertEqual(res['v3'], 3)
        self.assertEqual(res['v4'], 'five')
        self.assertEqual(res['v5'], 'c')

    def test_linguistics_example(self):
        """Test the linguistics abbreviations example from legacy tests."""
        abbreviations = [
            ['NP', 'abbreviates', 'kim', 'sany', 'lee'],
            ['DET', 'abbreviates', 'a', 'the', 'her'],
            ['N', 'abbreviates', 'consumer', 'man', 'woman'],
            ['BV', 'abbreviates', 'is', 'was']
        ]
        v1__ = var_many()
        v2__ = var_many('v2')
        v3__ = var_many('v3')
        v4__ = var_many()

        cat = 'N'
        word = 'consumer'
        res = matches(abbreviations, [v1__, [cat, 'abbreviates', v2__, word, v3__], v4__])
        self.assertEqual(res['v2'], [])
        self.assertEqual(res['v3'], ['man', 'woman'])

    def test_global_interaction(self):
        """Test enable/disable/clear globals."""
        # Test disabled
        disable_globals()
        v1_ = var_one('v1_test')
        matches([1, 2], [1, v1_])
        self.assertFalse(hasattr(builtins, 'v1_test'))

        # Test enabled
        enable_globals()
        matches([1, 100], [1, v1_])
        self.assertTrue(hasattr(builtins, 'v1_test'))
        self.assertEqual(getattr(builtins, 'v1_test'), 100)

        # Test clear
        clear_globals()
        self.assertFalse(hasattr(builtins, 'v1_test'))


if __name__ == '__main__':
    unittest.main()
