from popmatches import var_many, var_one, mexp, match_procedure


def test_var_one_many():

    print('wild_matchmany' == var_many().vtype)
    print('var_matchmany' == var_many(vname='v').vtype)
    print('wild_proc_matchmany' == var_many(proc=True).vtype)
    print('var_proc_matchmany' == var_many(vname='v', proc=True).vtype)
    print('wild_n_matchmany' == var_many(n=2).vtype)
    print('var_n_matchmany' == var_many(vname='v', n=2).vtype)
    print('wild_proc_n_matchmany' == var_many(n=2, proc=True).vtype)
    print('var_proc_n_matchmany' == var_many(vname='v', n=2, proc=True).vtype)

    print('wild_matchone' == var_one().vtype)
    print('var_matchone' == var_one('v').vtype)
    print('wild_proc_matchone' == var_one(proc=True).vtype)
    print('var_proc_matchone' == var_one('v', proc=True).vtype)


def test_mexp():

    print(mexp("??XY:one_two:2").vtype == 'var_proc_n_matchmany')
    print(mexp("??XY:one_two").vtype == 'var_proc_matchmany')
    print(mexp("??XY:2").vtype == 'var_n_matchmany')
    print(mexp("??XY").vtype == 'var_matchmany')
    print(mexp("==:one_two:2").vtype == 'wild_proc_n_matchmany')
    print(mexp("==:one_two").vtype == 'wild_proc_matchmany')
    print(mexp("==:2").vtype == 'wild_n_matchmany')
    print(mexp("==").vtype == 'wild_matchmany')
    print(mexp("?XY:one_two").vtype == 'var_proc_matchone')
    print(mexp("?XY").vtype == 'var_matchone')
    print(mexp("=:one_two").vtype == 'wild_proc_matchone')
    print(mexp("=").vtype == 'wild_matchone')


if __name__ == '__main__':

    @match_procedure
    def one_two(l):
        if l == [1, 2]:
            return "one_two"
        else:
            return False

    test_var_one_many()
    test_mexp()