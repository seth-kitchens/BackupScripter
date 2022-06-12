import gplib

g_int = 0
g_dict = {}
g_set = set()

def a(x='DBG'): print('a:', x)
def b(x='DBG'): print('  b:', x)
def c(x='DBG'): print('    c:', x)
def d(x='DBG'): print('      d:', x)

def print_stop(*args):
    print(*args)
    print("DBG Stop > ", end="")
    input()

# for making easy to find dbg print statements, 'debug_utils.p() or ddd.p() instead of print()'
def p(*args, **kwargs):
    print(*args, **kwargs)

# print objects
def po(*args, pre='DBG Objs: '):
    print(pre, end='')
    if not args:
        print('None')
        return
    indent = ' ' * len(pre)
    print(args[0])
    for i in range(1, len(args)):
        print(indent + str(args[i]))

# print locals
def pl(locals, pre='DBG locals: '):
    print(pre, end='')
    if not locals:
        print('None')
    indent = ' ' * len(pre)
    ks = list(locals.keys())
    longest = 0
    for k in ks:
        if len(k) > longest:
            longest = len(k)
    for i in range(len(ks)):
        if i > 0:
            print(indent, end='')
        print(ks[i] + ': '.ljust(longest - len(ks[i]) + 2) + str(locals[ks[i]]))

def prompt_any_input(text='Enter any input to continue.'):
    print(text)
    print('> ', end='')
    input()
    return

def if_in_print(a, b, *args, label='DBG: '):
    if a in b:
        print(label, end='')
        print(a, 'is in', b, end='')
        if args:
            print(',', *args, end='')
        print()
        return True
    return False

def handle_event(context):
    if gplib.g.debug.do_print_events:
        print('DBG: event: ' + str(context.event) + ', values: ' + str(context.values))

def pause():
    while True:
        pass

def print_diff_dict_keys(arg_d1, arg_d2):
    from gplib.text import utils as text_utils
    d1 = arg_d1.copy()
    d2 = arg_d2.copy()
    to_pop = []
    for k, v in d1.items():
        if k in d2.keys():
            to_pop.append(k)
    for k in to_pop:
        d1.pop(k)
        d2.pop(k)
    #print('d1:', d1)
    #print('d2:', d2)
    #text_utils.print_dicts_side_by_side(d1, d2)
    text_utils.print_side_by_side([list(d1.keys()), list(d2.keys())])
    print('d1 len:', len(d1))
    print('d2 len:', len(d2))