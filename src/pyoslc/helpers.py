def build_uri(base, *parts):
    """
    This method helps to generate a URI based on a list of words
    passed as a parameter
    :param base: The URI base e.g.: http://examples.com
    :param parts: List of elementos for generatig the URI e.g.: [oooooslc,service,catalog]
    :return: The URI formed with the base and the parts e.g.: http://examples.com/oooooslc/service/catalog
    """
    if parts:
        base = base + '/'.join(parts)
    return base
