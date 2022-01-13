import os

# https://docs.python.org/3/library/stdtypes.html#str.removeprefix
def remove_prefix(string: str, prefix: str) -> str:
    return string[len(prefix):]

def is_path_under_directory(path: str, directory_path: str) -> bool:
    return os.path.relpath(path).startswith(os.path.relpath(directory_path)) 
