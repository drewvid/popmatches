import unittest
from collections import OrderedDict
from popmatches import (
    matches, smatches, mexp, disable_globals, enable_globals, 
    clear_globals, match_procedure, V, MatchVar
)

class TestPopmatchesComprehensive(unittest.TestCase):

    def setUp(self):
        # Ensure a clean state for each test
        clear_globals()
        enable_globals()
        V.clear()

    # 1. Basic Literals
    def test_basic_literals(self):
        self.assertTrue(matches([1, 2, 3], [1, 2, 3]))
        self.assertTrue(matches(["a", "b"], ["a", "b"]))
        self.assertFalse(matches([1, 2], [1, 3]))
        self.assertFalse(matches([1, 2], [1, 2, 3]))

    # 2. Wildcards
    def test_wildcards(self):
        # ? matches one
        self.assertTrue(matches([1, 2, 3], [1, mexp("?"), 3]))
        # ?? matches many
        self.assertTrue(matches([1, 2, 3, 4], [1, mexp("??"), 4]))
        self.assertTrue(matches([1, 4], [1, mexp("??"), 4])) # matches zero items
        # == matches many
        self.assertTrue(matches([1, 2, 3, 4], [1, mexp("=="), 4]))

    # 3. Variable Binding
    def test_variable_binding(self):
        # MatchOne binding
        res = matches([1, 2, 3], [1, mexp("?X"), 3])
        self.assertIsInstance(res, OrderedDict)
        self.assertEqual(res['X'], 2)
        
        # MatchMany binding
        res = matches([1, 2, 3, 4], [1, mexp("??Y"), 4])
        self.assertEqual(res['Y'], [2, 3])
        
        # Multiple bindings
        res = smatches("head mid1 mid2 tail", "?H ??M tail")
        self.assertEqual(res['H'], "head")
        self.assertEqual(res['M'], ["mid1", "mid2"])

    # 4. N-Item Matches
    def test_n_item_matches(self):
        # Match exactly 2
        res = matches([1, 2, 3, 4, 5], [1, mexp("??X:2"), 4, 5])
        self.assertEqual(res['X'], [2, 3])
        
        # Fails if count doesn't match
        self.assertFalse(matches([1, 2, 3, 4, 5], [1, mexp("??X:4"), 5]))

    # 5. Procedural Matches
    def test_procedural_matches(self):
        @match_procedure
        def is_even(x):
            return x % 2 == 0

        @match_procedure
        def starts_with_a(s):
            return s if s.startswith('a') else False

        # One with proc (shorthand ?:proc)
        self.assertTrue(matches([1, 2, 3], [1, mexp("?:is_even"), 3]))
        self.assertFalse(matches([1, 3, 3], [1, mexp("?:is_even"), 3]))
        
        # One with vname and proc
        res = matches(["apple", "banana"], [mexp("?X:starts_with_a"), "banana"])
        self.assertEqual(res['X'], "apple")
        
        # Many with proc
        @match_procedure
        def all_digits(l):
            return all(isinstance(x, int) for x in l)
            
        self.assertTrue(matches([1, 2, 3, "end"], [mexp("??X:all_digits"), "end"]))

    # 6. Nested Structures
    def test_nested_structures(self):
        data = [1, [2, 3], 4]
        pattern = [1, [2, mexp("?X")], 4]
        res = matches(data, pattern)
        self.assertEqual(res['X'], 3)
        
        data = [[1, 2], [3, 4]]
        pattern = [[1, mexp("?A")], [mexp("?B"), 4]]
        res = matches(data, pattern)
        self.assertEqual(res['A'], 2)
        self.assertEqual(res['B'], 3)
        
        # Complex nesting
        data = ["a", ["b", ["c", "d"]], "e"]
        pattern = ["a", ["b", mexp("??Inner")], "e"]
        res = matches(data, pattern)
        self.assertEqual(res['Inner'], [["c", "d"]])

    # 7. Boundary & Edge Cases
    def test_edge_cases(self):
        # Empty inputs
        self.assertTrue(matches([], []))
        self.assertFalse(matches([1], []))
        self.assertFalse(matches([], [1]))
        
        # MatchMany at the end
        res = smatches("1 2 3 4", "1 ??Rest")
        self.assertEqual(res['Rest'], ["2", "3", "4"])
        
        # MatchMany at the beginning
        res = smatches("1 2 3 4", "??Start 4")
        self.assertEqual(res['Start'], ["1", "2", "3"])
        
        # MatchMany matching nothing
        res = smatches("1 2", "1 ??Empty 2")
        self.assertEqual(res['Empty'], [])

    # 8. Global Injection
    def test_global_injection(self):
        # Enabled by default (set in setUp)
        smatches("hello world", "?Greeting ?Target")
        
        # Check if Greeting and Target are in builtins/globals
        import builtins
        self.assertEqual(builtins.__dict__.get('Greeting'), "hello")
        self.assertEqual(builtins.__dict__.get('Target'), "world")
        
        # Disable globals
        disable_globals()
        smatches("bye bye", "?Parting ?Who")
        self.assertIsNone(builtins.__dict__.get('Parting'))
        
        # Clear globals
        enable_globals()
        smatches("foo bar", "?Var1 ?Var2")
        self.assertEqual(builtins.__dict__.get('Var1'), "foo")
        clear_globals()
        self.assertIsNone(builtins.__dict__.get('Var1'))

    # 9. Error and Negative Cases
    def test_negative_cases(self):
        # Type mismatch: list vs atom
        self.assertFalse(matches([1, 2], [[1, 2]]))
        self.assertFalse(matches([[1, 2]], [1, 2]))
        
        # Pattern too long
        self.assertFalse(matches([1, 2], [1, 2, 3]))
        
        # Pattern too short
        self.assertFalse(matches([1, 2, 3], [1, 2]))

if __name__ == '__main__':
    unittest.main()
