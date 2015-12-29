# TODO: This can't live in .util until the circular import of
#       core -> util -> localtime -> win32 -> core is resolved.


class Memoized(type):
    """
    Metaclass for memoization based on __init__ args/kwargs.
    """

    def __new__(mcs, name, bases, dict):
        if "_cache" not in dict:
            dict["_cache"] = {}
        return type.__new__(mcs, name, bases, dict)

    def __memoized_init__(cls, *args, **kwargs):
        if hasattr(cls, "_get_memo_key"):
            key = cls._get_memo_key(args, kwargs)
        else:
            key = (args or None, frozenset(kwargs.items()) or None)
        if key not in cls._cache:
            cls._cache[key] = type.__call__(cls, *args, **kwargs)
        return cls._cache[key]

    __call__ = __memoized_init__  # This aliasing makes tracebacks more understandable.
