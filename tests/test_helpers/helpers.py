def contains_(a, b):
    if b not in a:
        raise AssertionError("%r not in %r" % (b, a))
