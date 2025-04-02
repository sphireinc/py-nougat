from typing import Any, List, Optional, Tuple, Union, Callable, TypeVar, cast
from functools import lru_cache

T = TypeVar('T')


# Sentinel object for distinguishing between None and missing values
_SENTINEL = object()


def nougat(data: Any,
               *keys: Union[str, int, Tuple[Union[str, int], ...]],
               default: Any = None,
               separator: Optional[str] = None,
               transform: Optional[Callable[[Any], Any]] = None,
               strict_types: bool = False) -> Any:
    """
    High-performance function to access deeply nested values in data structures.

    Args:
        data: Source data structure (dict, list, or object with __getitem__)
        *keys: Keys to traverse. Can be:
               - Individual keys (strings/integers)
               - Tuples of keys to try alternatives (returns first match)
               - Dot-separated string paths when separator is provided
        default: Value to return if path doesn't exist
        separator: If provided, splits string keys on this character
        transform: Optional function to transform final value
        strict_types: If True, fails with TypeError on invalid intermediate types

    Returns:
        The value at the specified path or default if not found

    Examples:
        nougat(data, "users", 0, "name")
        nougat(data, "users.0.name", separator=".")
        nougat(data, ("user", "admin"), "settings") # Tries user.settings then admin.settings
    """
    if not keys:
        return data

    # Handle dot notation for paths
    if separator is not None and len(keys) == 1 and isinstance(keys[0], str):
        keys = tuple(keys[0].split(separator))

    try:
        result = data
        for key in keys:
            # Handle tuple of alternative keys
            if isinstance(key, tuple):
                for alt_key in key:
                    try:
                        if hasattr(result, 'get') and not isinstance(result, (list, tuple)):
                            result = result.get(alt_key)
                            break
                        else:
                            result = result[alt_key]
                            break
                    except (KeyError, IndexError, TypeError):
                        continue
                else:  # No matches found in alternatives
                    result = default
                continue

            # Fast path for dicts
            if isinstance(result, dict):
                if key in result:
                    result = result[key]
                else:
                    result = default
            # Handle lists/tuples with integer indices
            elif isinstance(result, (list, tuple)) and isinstance(key, int):
                if 0 <= key < len(result):
                    result = result[key]
                else:
                    result = default
            # Handle objects with get method (like dict)
            elif hasattr(result, 'get') and not isinstance(result, (list, tuple)):
                result = result.get(key, _SENTINEL)
                if result is _SENTINEL:
                    result = default
            # Handle objects with __getitem__ (subscriptable)
            elif hasattr(result, '__getitem__'):
                try:
                    result = result[key]
                except (KeyError, IndexError, TypeError):
                    try:
                        result = result[int(key)]
                    except (KeyError, IndexError, TypeError):
                        result = default
            else:
                if strict_types:
                    raise TypeError(f"Cannot traverse {type(result).__name__} with key {key}")
                result = default
        res = transform(result) if transform else result
        return res

    except Exception:  # Catch any unexpected errors to ensure function doesn't raise
        return transform(result) if transform else result


# Create a cached version for frequently accessed paths
@lru_cache(maxsize=128)
def _make_path_accessor(path: Tuple[Union[str, int, Tuple[Union[str, int], ...]], ...],
                        separator: Optional[str] = None,
                        strict: bool = False) -> Callable[[Any, Any, Optional[Callable]], Any]:
    """Creates optimized accessor function for a specific path"""

    def accessor(data: Any, default: Any = None, transform: Optional[Callable] = None) -> Any:
        return nougat(data, *path, default=default, separator=separator,
                          transform=transform, strict_types=strict)

    return accessor


def nougat_cached(path_components: Union[str, List[Union[str, int, Tuple]]],
                      separator: Optional[str] = None,
                      strict: bool = False) -> Callable:
    """
    Returns a cached function to efficiently retrieve the same path repeatedly.

    Args:
        path_components: Either a dot-separated string or a list of path components
        separator: Separator for string paths (default: None)
        strict: Whether to use strict type checking

    Returns:
        A function that takes (data, default=None, transform=None) and returns the nested value
    """
    if isinstance(path_components, str) and separator:
        # path = tuple(path_components.split(separator)) # mypy doesn't like this
        path = tuple(cast(Union[str, int, Tuple], p) for p in path_components.split(separator))  # ✅ Fix: Cast elements properly
    else:
        path = tuple(path_components if isinstance(path_components, (list, tuple)) else [path_components])

    return _make_path_accessor(path, separator, strict)