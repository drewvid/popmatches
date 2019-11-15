from popmatches import smatches, matches, disable_globals, enable_globals, clear_globals
from popmatches import var_one, var_many, V, mexp, register_match_procedure


def test_smatches():

    pattern_pairs = [
        # No bindings
        ('1 2 3 4', '=='),
        ('1', '== 1 =='),
        ('1 2', '== 2 =='),
        ('2 3', '== 2 =='),
        ('1 2 3', '== 2 =='),
        ('1', '='),
        ('1 2 3', '= 2 ='),
        # Bindings
        ('1 2 3 4', '?X 2 ??Y'),
        ('1 2 3 4', '??X:1 2 ??Y'),
        ('1 2 3 4', '??X:2 3 ?Y'),
        ('1 2 3 4 5', '??X 3 ??Y'),
        ('3', '??X 3 ??Y'),
        ('3', '== 3 ??Y'),
        ('2 3', '??X 3 ??Y'),
        ('3 4', '??X 3 ??Y'),
        ('1 2 3', '?X 2 ?Y'),
        ('1 2 3', '??X:1 2 ??Y:1'),
        ('1 2 3 4 5 [6(pos)] 7 8 9 10', '= 2 == 5 ?X ??Y:2 ??Z'),
        # No Match
        ('3', '?X 3 ?Y'),
        ('2 3', '?X 3 ?Y'),
        ('3 4', '?X 3 ?Y'),
        ('1', '= 1 ='),
        ('1 2 3', '= 2'),
        ('1 2 3', '2 ='),
        ('1', '== 1 2 =='),
        ('1 2 3', '== 2'),
        ('1 2 3', '2 =='),
        ('hello', 'perhaps ??X'),
    ]

    for item in pattern_pairs:
        text = item[0]
        pattern = item[1]
        res = smatches(text, pattern)
        print(', '.join(item))
        print('\t', res)


def test_matches():

    v1p_ = var_one(proc=zero)
    v2_ = var_one()
    v3_ = var_one(vname='v3')
    v4p_ = var_one(vname='v4', proc=five)
    v5_ = var_one(vname='v5')

    res = matches([0, 1, 2, 3, 4, 5, [['a', 'b'], 'c']], [ v1p_, v2_, 2, v3_, 4, v4p_, [['a', 'b'], v5_]])
    print(res)

    v1__ = var_many()
    v2__ = var_many()
    res = matches([1, 2, 3, 4, 5], [v1__, 3, v2__])
    print(res)

    v1__ = var_many(vname='v1', proc=one_two)
    v2__ = var_many(vname='v2', n=2, proc=three_four)
    res = matches([1, 2, 3, 4, 5], [v1__, 3, v2__])
    print(res)

    v1__ = var_many('v1')
    v2__ = var_many('v2')
    v3__ = var_many('v3')
    res = matches([[1], [2], [3, 'a', 'b'], [4], [5]], [v1__, [3, v2__], v3__])
    print(res)

    abbreviations = [['NP', 'abbreviates', 'kim', 'sany', 'lee'],
                     ['DET', 'abbreviates', 'a', 'the', 'her'],
                     ['N', 'abbreviates', 'consumer', 'man', 'woman'],
                     ['BV', 'abbreviates', 'is', 'was'],
                     ['CNJ', 'abbreviates', 'and', 'or'],
                     ['ADJ', 'abbreviates', 'happy', 'stupid'],
                     ['MOD', 'abbreviates', 'very'],
                     ['ADV', 'abbreviates', 'often', 'always', 'sometimes']]

    v1__ = var_many()
    v2__ = var_many('v2')
    v3__ = var_many('v3')
    v4__ = var_many()

    cat = 'N'
    word = 'consumer'
    res = matches(abbreviations, [v1__, [cat, 'abbreviates', v2__, word, v3__], v4__])
    print(res)

    cat = 'MOD'
    word = 'very'
    res = matches(abbreviations, [v1__, [cat, 'abbreviates', v2__, word, v3__], v4__])
    print(res)

    print()
    matches([1,2,3,4], [mexp("?hd"), mexp("??tl")])
    print("head and tail of [1,2,3,4] is:", hd, tl)


def test_V(): 

    disable_globals()
    v1_ = var_one('v1')
    v2__ = var_many('v2')
    res = matches([1, [2, 3], 4, 5], [1, v1_, v2__])
    print("mspace", V['v1'], V['v2'])
    try:
        print(v1, v2)
    except:
        print("global variables disabled")
    print()

    enable_globals()
    v1_ = var_one('v1')
    v2__ = var_many('v2')
    res = matches([1, [2, 3], 4, 5], [1, v1_, v2__])
    print("mspace", V['v1'], V['v2'])
    print(v1, v2)

    clear_globals()
    try:
        print(v1, v2)
    except:
        print("global variables cleared")

    print()

    enable_globals()
    print("global variables enabled")
    v1_ = var_one('v1')
    v2__ = var_many('v2')
    res = matches([1, [2, 3], 4, 5], [1, v1_, v2__])
    print("mspace", V['v1'], V['v2'])
    print(v1, v2)


if __name__ == '__main__':

    def zero(x):
        if x == 0:
            return 'zero'
        else:
            return False

    def five(x):
        if x == 5:
            return 'five'
        else:
            return False

    def one_two(l):
        if l == [1, 2]:
            return "one_two"
        else:
            return False

    def three_four(l):
        if l == [4, 5]:
            return "four_five"
        else:
            return False

    register_match_procedure('zero', zero)
    register_match_procedure('five', five)
    register_match_procedure('one_two', one_two)
    register_match_procedure('three_four', three_four)

    test_smatches()
    print()
    print()
    test_matches()
    print()
    print()
    test_V()
