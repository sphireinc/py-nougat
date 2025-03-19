# nougat.py
# This module provides a utility function for dynamically adding a method 
# (`nougat`) to any object, allowing for safe access of deeply nested 
# dictionary values. The `nougat` method iterates through a list of keys 
# to retrieve the corresponding value, with customizable default behavior.
# 
# Usage:
# - Call `initNougat(obj)` to add the `nougat` method to an object `obj`.
# - Once initialized, `obj.nougat(*keys, default=None)` can be used to retrieve nested 
#   values from the object.

from typing import Any, Dict, Optional, TypeVar, Union, overload, cast
import types

T = TypeVar('T', bound=Dict[str, Any])

def nougat(self: Dict[str, Any], *keys: str, default: Any = None) -> Any:
    """
    Safely access deeply nested dictionary values.
    
    Args:
        *keys: A sequence of keys to traverse
        default: Value to return if any key is missing (default: None)
        
    Returns:
        The value at the nested location or the default value
    """
    result = self
    for i, key in enumerate(keys):
        if not hasattr(result, 'get'):
            # If we're at an intermediate value that isn't a dict-like object
            return default
        
        # For the last key, use the provided default
        if i == len(keys) - 1:
            return result.get(key, default)
        
        # For intermediate keys, use empty dict as default to continue traversal
        result = result.get(key, {})
    
    return result


# Author Note: Monkey Patch Central, but works for Airflow
def init_nougat_global() -> None:
    """Globally add nougat method to all dictionary instances."""
    if not hasattr(dict, 'nougat'):
        setattr(dict, 'nougat', lambda self, *args, default=None: nougat(self, *args, default=default))

# Author Note: Another Monkey Patch solution for when you can't modify dict
def nougat_patch() -> None:
    """Monkey-patch dictionary instances with the `nougat` method globally."""

    # Original __getitem__ reference
    original_getitem = dict.__getitem__

    def patched_getitem(self, key):
        """Wrapper that adds nougat dynamically when accessed."""
        # Attach nougat once per dictionary instance
        if not hasattr(self, 'nougat'):
            # Use types.MethodType to bind it to the instance
            import types
            self.nougat = types.MethodType(nougat, self)

        return original_getitem(self, key)

    # Monkey-patch all dict instances by replacing __getitem__
    dict.__getitem__ = patched_getitem


def init_nougat(obj: T) -> T:
    """
    Add the nougat method to an object.
    
    Args:
        obj: Any object that supports dict-like behavior with get() method
        
    Raises:
        AttributeError: If obj doesn't support the get() method
    """
    # Check if object can support nougat operations
    if not hasattr(obj, 'get'):
        raise AttributeError("Object must support dict-like 'get' method")
    obj.nougat = types.MethodType(nougat, obj)  # type: ignore
    return obj
