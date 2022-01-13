# https://docs.python.org/3/library/stdtypes.html#str.removeprefix
def remove_prefix(string: str, prefix: str):
    return string[len(prefix):]
