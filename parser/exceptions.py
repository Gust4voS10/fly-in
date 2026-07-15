"""Custom exceptions for the map parser."""


class ParserError(Exception):
    """Raised when a map file cannot be parsed correctly.

    This covers missing files, malformed instructions, invalid metadata,
    unknown zone references, and any other issue that prevents building a
    valid :class:`core.graph.Graph` from the map file.
    """
    pass
