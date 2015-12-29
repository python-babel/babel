# TODO: This can't live in .util until the circular import of
#       core -> util -> localtime -> win32 -> core is resolved.


class Memoized(type):
    """
    Metaclass for memoization based on __init__ args/kwargs.
    """

    def __new__(mcs, name, bases, dict):
        if "_cache" not in dict:
            dict["_cache"] = {}
        if "_cache_lock" not in dict:
            dict["_cache_lock"] = None
        return type.__new__(mcs, name, bases, dict)

    def __memoized_init__(cls, *args, **kwargs):
        lock = cls._cache_lock
        if hasattr(cls, "_get_memo_key"):
            key = cls._get_memo_key(args, kwargs)
        else:
            key = (args or None, frozenset(kwargs.items()) or None)

        try:
            return cls._cache[key]
        except KeyError:
            try:
                if lock:
                    lock.acquire()
                inst = cls._cache[key] = type.__call__(cls, *args, **kwargs)
                return inst
            finally:
                if lock:
                    lock.release()

    __call__ = __memoized_init__  # This aliasing makes tracebacks more understandable.
