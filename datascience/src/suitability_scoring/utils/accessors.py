def get_val(obj, key, default=None):
    """
    Retrieves a value from either a dictionary or an object attribute.

    This allows the scoring engine to remain agnostic of the data source,
    supporting both CSV-loaded dictionaries (CLI mode) and SQLAlchemy
    ORM models (API mode).

    :param obj: Source record, either a dictionary or an object instance.
        If ``None``, ``default`` is returned.
    :param key: Field name to look up. For dictionaries this is the dict key;
        for objects this is the attribute name.
    :param default: Fallback value returned when ``obj`` is ``None`` or when
        ``key`` is missing from the source.
    :returns: The resolved value from ``obj`` for ``key``, otherwise ``default``.
    """
    if obj is None:
        return default
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)
