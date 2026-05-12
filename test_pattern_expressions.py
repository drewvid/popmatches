import unittest
from popmatches import var_many, var_one, mexp, match_procedure

class TestPatternExpressions(unittest.TestCase):
    """Tests for MatchVar creation and shorthand expression parsing (mexp)."""

    def test_var_one_many_types(self):
        """Verify that var_one and var_many correctly set internal vtype strings."""
        dummy_proc = lambda x: True
        
        self.assertEqual(var_many().vtype, 'wild_matchmany')
        self.assertEqual(var_many(vname='v').vtype, 'var_matchmany')
        self.assertEqual(var_many(proc=dummy_proc).vtype, 'wild_proc_matchmany')
        self.assertEqual(var_many(vname='v', proc=dummy_proc).vtype, 'var_proc_matchmany')
        self.assertEqual(var_many(n=2).vtype, 'wild_n_matchmany')
        self.assertEqual(var_many(vname='v', n=2).vtype, 'var_n_matchmany')
        self.assertEqual(var_many(n=2, proc=dummy_proc).vtype, 'wild_proc_n_matchmany')
        self.assertEqual(var_many(vname='v', n=2, proc=dummy_proc).vtype, 'var_proc_n_matchmany')

        self.assertEqual(var_one().vtype, 'wild_matchone')
        self.assertEqual(var_one('v').vtype, 'var_matchone')
        self.assertEqual(var_one(proc=dummy_proc).vtype, 'wild_proc_matchone')
        self.assertEqual(var_one('v', proc=dummy_proc).vtype, 'var_proc_matchone')

    def test_mexp_parsing(self):
        """Verify that shorthand strings are correctly parsed into MatchVars."""
        # Registration for proc names used in shorthand
        @match_procedure
        def one_two(l):
            return l == [1, 2]

        self.assertEqual(mexp("??XY:one_two:2").vtype, 'var_proc_n_matchmany')
        self.assertEqual(mexp("??XY:one_two").vtype, 'var_proc_matchmany')
        self.assertEqual(mexp("??XY:2").vtype, 'var_n_matchmany')
        self.assertEqual(mexp("??XY").vtype, 'var_matchmany')
        self.assertEqual(mexp("==:one_two:2").vtype, 'wild_proc_n_matchmany')
        self.assertEqual(mexp("==:one_two").vtype, 'wild_proc_matchmany')
        self.assertEqual(mexp("==:2").vtype, 'wild_n_matchmany')
        self.assertEqual(mexp("==").vtype, 'wild_matchmany')
        self.assertEqual(mexp("?XY:one_two").vtype, 'var_proc_matchone')
        self.assertEqual(mexp("?XY").vtype, 'var_matchone')
        self.assertEqual(mexp("=:one_two").vtype, 'wild_proc_matchone')
        self.assertEqual(mexp("=").vtype, 'wild_matchone')


if __name__ == '__main__':
    unittest.main()