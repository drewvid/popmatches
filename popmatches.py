import sys
from collections import OrderedDict
import re
from pprint import pprint

create_global_variables = True
defined_global_variables = set()
match_cache = None


#
# Match Vars and Expressions
#

V = OrderedDict()

def match_type(one_or_many, vname, nitems, proc):

    if one_or_many == 'many':
        if(nitems == -1):
            if vname is None and proc is None:
                vtype = 'wild_matchmany'
            elif vname is not None and proc is None:
                vtype = 'var_matchmany'
            elif vname is None and proc is not None:
                vtype = 'wild_proc_matchmany'
            elif vname is not None and proc is not None:
                vtype = 'var_proc_matchmany'
        else:
            if vname is None and proc is None:
                vtype = 'wild_n_matchmany'
            elif vname is not None and proc is None:
                vtype = 'var_n_matchmany'
            elif vname is None and proc is not None:
                vtype = 'wild_proc_n_matchmany'
            elif vname is not None and proc is not None:
                vtype = 'var_proc_n_matchmany'
    else:
        if vname is None and proc is None:
            vtype = 'wild_matchone'
        elif vname is not None and proc is None:
            vtype = 'var_matchone'
        elif vname is None and proc is not None:
            vtype = 'wild_proc_matchone'
        elif vname is not None and proc is not None:
            vtype = 'var_proc_matchone'

    return vtype


class MatchVar(object):

    def __init__(self, one_or_many, vname=None, nitems=-1, proc=None):
        self.one_or_many = one_or_many
        self.vname = vname
        self.vtype = match_type(one_or_many, vname, nitems, proc)
        self.nitems = nitems
        self.proc  = proc

    def __str__(self):
        if self.vname:
            return self.vname
        else:
            return 'None'

    def __repr__(self):
        if self.one_or_many == "many":
            return '({0}, {1}, {2}, {3})'.format(self.vname, self.proc, self.nitems, self.vtype)
        else:
            return '[{0}, {1}, {2}]'.format(self.vname, self.proc, self.vtype)


def ismexp(v):
    return isinstance(v, MatchVar)


def ismany(v):
    return v.one_or_many == 'many'


def isone(v):
    return v.one_or_many == 'one'


def var_one(vname=None, proc=None):
    return MatchVar('one', vname=vname, proc=proc)


def var_many(vname=None, proc=None, n=-1):
    return MatchVar('many', vname=vname, nitems=n, proc=proc)


U_ = var_one('u')
V_ = var_one('v')
W_ = var_one('w')
X__ = var_many('x')
Y__ = var_many('y')
Z__ = var_many('z')
A_ = var_one()
A__ = var_many()


def mexp(s):

    vname = None
    proc = None
    n = -1

    m = re.match("(\?\??|==?)([\w]*)?:?([\w]*)?:?([\w]*)?", s)
    if not m:
        return s
    res = m.groups()

    opp = res[0]
    if res[1] != '':
        vname = res[1]
    if res[2] != '':
        if res[2].isdigit():
            n = int(res[2])
        else:
            proc = globals()[res[2]]
    if res[3] != '':
        n = int(res[3])

    if '==' in opp or '??' in opp:
        if vname or proc or n:
            return var_many(vname=vname, proc=proc, n=n)
        else:
            return A__
    elif '=' in opp or '?' in opp:
        if vname or proc:
            return var_one(vname=vname, proc=proc)
        else:
            return A_


#
# The popmatcher
#


class SetGlobal:

    def __init__(self):
        try:
            self.__dict__['builtin'] = sys.modules['__builtin__'].__dict__
        except KeyError:
            self.__dict__['builtin'] = sys.modules['builtins'].__dict__

    def setattr(self, name, value):
        self.builtin[name] = value

    def delattr(self, name):
        del self.builtin[name]


sg = SetGlobal()


def clear_globals():
    global sg, defined_global_variables
    for name in defined_global_variables:
        sg.delattr(name)
    defined_global_variables = set()


def disable_globals():
    global create_global_variables, sg, defined_global_variables
    if create_global_variables:
        create_global_variables = False
        for name in defined_global_variables:
            sg.delattr(name)
        defined_global_variables = set()


def enable_globals():
    global create_global_variables, sg
    if create_global_variables is False:
        create_global_variables = True


def assign(name, value):
    if create_global_variables:
        global sg
        sg.setattr(name, value)
        defined_global_variables.add(name)
    V[name] = value


def register_match_procedure(name, proc):
    globals()[name] = proc


def eval_bind_one(current_s, current_p, bindings):

    if current_p.vtype == 'wild_matchone':
        valid = True
    elif current_p.vtype == 'var_matchone':
        assign(current_p.vname, current_s)
        bindings[current_p.vname] = current_s
        valid = True
    elif current_p.vtype == 'wild_proc_matchone':
        valid = current_p.proc(current_s)
    elif current_p.vtype == 'var_proc_matchone':
        valid = current_p.proc(current_s)
        if valid:
            assign(current_p.vname, valid)
            bindings[current_p.vname] = valid
    else:
        print("this should not happen")
        valid = False

    return bool(valid)


def eval_bind_many(current_p, value, bindings):

    valid = True

    if current_p.nitems == -1:
        if current_p.vtype == 'wild_matchmany':
            pass
        elif current_p.vtype == 'var_matchmany':
            assign(current_p.vname, value)
            bindings[current_p.vname] = value
        elif current_p.vtype == 'wild_proc_matchmany':
            valid = current_p.proc(value)
        elif current_p.vtype == 'var_proc_matchmany':
            valid = current_p.proc(value)
            if valid:
                assign(current_p.vname, valid)
                bindings[current_p.vname] = valid
    elif current_p.nitems > 0 and len(value) == current_p.nitems:
        if current_p.vtype == 'wild_n_matchmany':
            pass
        elif current_p.vtype == 'var_n_matchmany':
            assign(current_p.vname, value)
            bindings[current_p.vname] = value
        elif current_p.vtype == 'wild_proc_n_matchmany':
            valid = current_p.proc(value)
        elif current_p.vtype == 'var_proc_n_matchmany':
            valid = current_p.proc(value)
            if valid:
                assign(current_p.vname, valid)
                bindings[current_p.vname] = valid
    else:
        valid = False

    return bool(valid)


def gen_cache_index(l1, l2):
    return repr(l1) + repr(l2)


def get_index(current_p, s_tokens, s_index, p_tokens, p_index):

    if (current_p.nitems > 0):
        n = 0
        for index, item in enumerate(s_tokens[s_index:]):
            if n == current_p.nitems:
                break
            n += 1
    else:
        terminator = p_tokens[p_index + 1]
        for index, item in enumerate(s_tokens[s_index:]):
            if isinstance(terminator, list) and isinstance(item, list):
                bindings, amatch = new_matches(item, terminator)
                if amatch:
                    cache_index = gen_cache_index(item, terminator)
                    match_cache[cache_index] = bindings
                    break
            elif terminator == item:
                break

    return index


def new_matches(s_tokens, p_tokens):

    bindings = OrderedDict()

    amatch = True
    s_index = 0
    p_index = 0

    while s_index < len(s_tokens) and p_index < len(p_tokens) and amatch:

        current_p = p_tokens[p_index]
        current_s = s_tokens[s_index]

        if ismexp(current_p) and isone(current_p):
            amatch = eval_bind_one(current_s, current_p, bindings)
            s_index += 1
        elif ismexp(current_p) and ismany(current_p):
            if (p_index + 1) == len(p_tokens):
                tokens = s_tokens[s_index:]
                index = len(tokens)
            else:
                index = get_index(current_p, s_tokens, s_index, p_tokens, p_index)
                tokens = s_tokens[s_index:s_index + index]
            # items = [token[1] for token in tokens]
            items = tokens
            amatch = eval_bind_many(current_p, items, bindings)
            s_index += index
        elif isinstance(current_p, list) and isinstance(current_s, list):
            cache_index = gen_cache_index(current_s, current_p)
            if cache_index in match_cache:
                amatch = True
                b = match_cache[cache_index]
            else:
                b, amatch = new_matches(current_s, current_p)
            if amatch:
                bindings = OrderedDict(**bindings, **b)
            s_index += 1
        else:
            amatch = current_p == current_s
            s_index += 1
        p_index += 1

    if (p_index != len(p_tokens) or s_index != len(s_tokens)):
        if amatch:
            amatch = False
            if (len(s_tokens) == s_index and (len(p_tokens) - p_index) == 1):
                current_p = p_tokens[p_index]
                if ismany(current_p):
                    amatch = eval_bind_many(current_p, [], bindings)

    return bindings, amatch


def matches(data, pattern):
    global match_cache
    match_cache = OrderedDict()

    bindings, amatch = new_matches(data, pattern)

    if amatch and bindings:
        return bindings
    elif amatch:
        return True
    else:
        return False


def smatches(data_in, pattern_in):
    data = data_in.split()
    pattern = [mexp(item) for item in pattern_in.split()]
    return matches(data, pattern)


if __name__ == '__main__':

    print("Run test_matches.py")
