def build_uri(base, *parts):
    if parts:
        base = base + '/'.join(parts)
    return base
