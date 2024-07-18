from functools import partial


def find_entrypoints(group_name: str):
    """
    Find entrypoints of a given group using either `importlib.metadata` or the
    older `pkg_resources` mechanism.

    Yields tuples of the entrypoint name and a callable function that will
    load the actual entrypoint.
    """
    try:
        from importlib.metadata import entry_points
    except ImportError:
        pass
    else:
        eps = entry_points()
        if isinstance(eps, dict):  # Old structure before Python 3.10
            group_eps = eps.get(group_name, [])
        else:  # New structure in Python 3.10+
            group_eps = (ep for ep in eps if ep.group == group_name)
        for entry_point in group_eps:
            yield (entry_point.name, entry_point.load)
        return

    try:
        from pkg_resources import working_set
    except ImportError:
        pass
    else:
        for entry_point in working_set.iter_entry_points(group_name):
            yield (entry_point.name, partial(entry_point.load, require=True))
