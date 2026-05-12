import sys
import re
import builtins
from collections import OrderedDict
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple, Union, Set
from pprint import pprint

create_global_variables = True
defined_global_variables = set()
match_cache = None


#
# Match Vars and Expressions
#

V = OrderedDict()

class MatchCount(Enum):
    ONE = 'one'
    MANY = 'many'


def match_type(count: MatchCount, vname: Optional[str], nitems: int, proc: Optional[Callable]) -> str:
    """Determine the internal type string for a MatchVar."""
    prefix = "var" if vname else "wild"
    mid = "_proc" if proc else ""
    n_part = "_n" if (count == MatchCount.MANY and nitems != -1) else ""
    suffix = "matchmany" if count == MatchCount.MANY else "matchone"
    
    return f"{prefix}{mid}{n_part}_{suffix}"


class MatchVar(object):
    """
    Represents a variable or wildcard in a pattern.
    
    Attributes:
        count (MatchCount): Whether it matches ONE or MANY items.
        vname (str): The name of the variable to bind to.
        vtype (str): The internal type identifier.
        nitems (int): Exact number of items to match (for MANY matches).
        proc (callable): A procedural check function.
    """

    def __init__(self, count: MatchCount, vname: Optional[str] = None, nitems: int = -1, proc: Optional[Callable] = None):
        self.count = count
        self.vname = vname
        self.vtype = match_type(count, vname, nitems, proc)
        self.nitems = nitems
        self.proc = proc

    def __str__(self) -> str:
        return self.vname if self.vname else 'None'

    def __repr__(self) -> str:
        if self.count == MatchCount.MANY:
            return f'({self.vname}, {self.proc}, {self.nitems}, {self.vtype})'
        else:
            return f'[{self.vname}, {self.proc}, {self.vtype}]'


def ismexp(v: Any) -> bool:
    """Check if a value is a MatchVar."""
    return isinstance(v, MatchVar)


def ismany(v: MatchVar) -> bool:
    """Check if a MatchVar matches many items."""
    return v.count == MatchCount.MANY


def isone(v: MatchVar) -> bool:
    """Check if a MatchVar matches exactly one item."""
    return v.count == MatchCount.ONE


def var_one(vname: Optional[str] = None, proc: Optional[Callable] = None) -> MatchVar:
    """Create a MatchVar that matches one item."""
    return MatchVar(MatchCount.ONE, vname=vname, proc=proc)


def var_many(vname: Optional[str] = None, proc: Optional[Callable] = None, n: int = -1) -> MatchVar:
    """Create a MatchVar that matches many items."""
    return MatchVar(MatchCount.MANY, vname=vname, nitems=n, proc=proc)


U_ = var_one('u')
V_ = var_one('v')
W_ = var_one('w')
X__ = var_many('x')
Y__ = var_many('y')
Z__ = var_many('z')
A_ = var_one()
A__ = var_many()


def mexp(s: str) -> Union[MatchVar, str]:
    """
    Parse a shorthand string expression into a MatchVar.
    
    Examples:
        ?X        -> var_one('X')
        ??Y:5     -> var_many('Y', n=5)
        ?proc     -> var_one(proc=proc)
        ==        -> wildcard many
    """
    vname = None
    proc = None
    n = -1

    m = re.match(r"(\?\??|==?)([\w]*)?:?([\w]*)?:?([\w]*)?", s)
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
            # Look in calling module's globals or popmatches globals
            proc = globals().get(res[2])
            if not proc:
                # Fallback to check builtins if needed, but usually it's in popmatches globals
                # after being registered by @match_procedure
                pass

    if res[3] != '':
        n = int(res[3])

    if '==' in opp or '??' in opp:
        if vname or proc or n != -1:
            return var_many(vname=vname, proc=proc, n=n)
        else:
            return A__
    elif '=' in opp or '?' in opp:
        if vname or proc:
            return var_one(vname=vname, proc=proc)
        else:
            return A_
    return s


#
# The popmatcher
#


class SetGlobal:
    """Helper to inject variables into the global/builtin namespace."""

    def __init__(self):
        self.builtin_dict = builtins.__dict__

    def setattr(self, name: str, value: Any):
        """Set an attribute in the builtin namespace."""
        self.builtin_dict[name] = value

    def delattr(self, name: str):
        """Delete an attribute from the builtin namespace."""
        if name in self.builtin_dict:
            del self.builtin_dict[name]


sg = SetGlobal()


def clear_globals():
    """Clear all variables previously injected into the global namespace."""
    global defined_global_variables
    for name in defined_global_variables:
        sg.delattr(name)
    defined_global_variables = set()


def disable_globals():
    """Disable automatic global variable injection and clear existing ones."""
    global create_global_variables, defined_global_variables
    if create_global_variables:
        create_global_variables = False
        clear_globals()


def enable_globals():
    """Enable automatic global variable injection."""
    global create_global_variables
    create_global_variables = True


def assign(name: str, value: Any):
    """Assign a value to a variable, potentially injecting it into the global namespace."""
    if create_global_variables:
        sg.setattr(name, value)
        defined_global_variables.add(name)
    V[name] = value


def match_procedure(func: Callable) -> Callable:
    """Decorator to register a function as a match procedure."""
    globals()[func.__name__] = func
    return func


def eval_bind_one(current_s: Any, current_p: MatchVar, bindings: Dict[str, Any]) -> bool:
    """Evaluate and bind a single item match."""
    valid = False
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
        raise RuntimeError(f"Unexpected MatchVar vtype in eval_bind_one: {current_p.vtype}")

    return bool(valid)


def eval_bind_many(current_p: MatchVar, value: List[Any], bindings: Dict[str, Any]) -> bool:
    """Evaluate and bind a multi-item match."""
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


def gen_cache_index(l1: Any, l2: Any) -> str:
    """Generate a cache key for two objects."""
    return repr(l1) + repr(l2)


def get_index(current_p: MatchVar, s_tokens: List[Any], s_index: int, p_tokens: List[Any], p_index: int) -> int:
    """Find the index where a MANY match should stop."""
    index = 0
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
                    if match_cache is not None:
                        match_cache[cache_index] = bindings
                    break
            elif terminator == item:
                break

    return index


def new_matches(s_tokens: List[Any], p_tokens: List[Any]) -> Tuple[Dict[str, Any], bool]:
    """Recursive core matching logic."""
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
            items = tokens
            amatch = eval_bind_many(current_p, items, bindings)
            s_index += index
        elif isinstance(current_p, list) and isinstance(current_s, list):
            cache_index = gen_cache_index(current_s, current_p)
            if match_cache is not None and cache_index in match_cache:
                amatch = True
                b = match_cache[cache_index]
            else:
                b, amatch = new_matches(current_s, current_p)
            if amatch:
                bindings.update(b)
            s_index += 1
        else:
            amatch = current_p == current_s
            s_index += 1
        p_index += 1

    if amatch and (p_index != len(p_tokens) or s_index != len(s_tokens)):
        if (len(s_tokens) == s_index and (len(p_tokens) - p_index) == 1):
            current_p = p_tokens[p_index]
            if ismexp(current_p) and ismany(current_p):
                amatch = eval_bind_many(current_p, [], bindings)
            else:
                amatch = False
        else:
            amatch = False

    return bindings, amatch


def matches(data: List[Any], pattern: List[Any]) -> Union[Dict[str, Any], bool]:
    """
    Match a data list against a pattern list.
    
    Returns:
        - A dictionary of bindings if variables were matched.
        - True if the pattern matched but no variables were bound.
        - False if the pattern did not match.
    """
    global match_cache
    match_cache = OrderedDict()

    bindings, amatch = new_matches(data, pattern)

    if amatch:
        return bindings if bindings else True
    return False


def smatches(data_in: str, pattern_in: str) -> Union[Dict[str, Any], bool]:
    """
    Match a space-separated string against a shorthand pattern string.
    """
    data = data_in.split()
    pattern = [mexp(item) for item in pattern_in.split()]
    return matches(data, pattern)


if __name__ == '__main__':

    print("Run test_matches.py")
