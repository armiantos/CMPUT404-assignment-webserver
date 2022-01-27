import os
from constants import DEFAULT_ENCODING


def remove_prefix(string: str, prefix: str) -> str:
    """
    Removes a prefix substring from a given string

    Params:
    - `string` - The string to remove the prefix from
    - `prefix` - The substring to remove from the start of `string`

    Returns:
    A copy of `string` without the given `prefix`
    """
    # https://docs.python.org/3/library/stdtypes.html#str.removeprefix
    return string[len(prefix):]


def is_path_under_directory(path: str, directory_path: str) -> bool:
    """
    Checks if a given file is found under a given directory

    Params:
    - `path` - The path to the file to check
    - `directory_path` - The path to the directory to check from

    Returns:
    True if the `path` can be found under the `directory_path`, False otherwise
    """
    return os.path.relpath(path).startswith(os.path.relpath(directory_path))


def to_bytearray(string: str) -> bytearray:
    """
    Returns the utf-8 encoded bytearray for the given string

    Params:
    - `string` - The text to encode
    """
    return bytearray(string, DEFAULT_ENCODING)
