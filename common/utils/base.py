# Foundation level abstractions
import asyncio
from functools import wraps
import json
from typing import Any, Dict, List
import pandas as pd


class StrEnum:
    """
    An enumeration where members are also (and must be) strings.
    """

    def __init__(self, *args):
        self._members = set(args)
        for member in args:
            setattr(self, member, member)

    def __contains__(self, item):
        return item in self._members

    def __iter__(self):
        return iter(self._members)

    def __len__(self):
        return len(self._members)

    def __repr__(self):
        return f"{self.__class__.__name__}({', '.join(repr(member) for member in self._members)})"


def singleton(cls):
    """Class decorators for creating singletons"""
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance


def tryy(func, default=None):
    """
    A simple function decorator to catch exceptions and return the default value.

    Usage:
    - Add @tryy to any function and it will never throw an Exception.
    - Use higher order functions: new_fn = try(fname)
        - new_fn(args)
    """

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            return default

    return wrapper


class AsyncUtils:
    """Set of utils for working with async code"""

    @staticmethod
    def sync_wrapper(async_func):
        """
        A static method that creates a synchronous wrapper for an asynchronous function.

        Parameters:
            async_func (function): The asynchronous function to be wrapped.

        Returns:
            function: The synchronous wrapper function.

        Example:
            >>> async def async_func():
            ...     return "Async Result"
            >>> sync_wrapper(async_func)()
            'Async Result'
        """

        @wraps(async_func)
        def wrapper(*args, **kwargs):
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(async_func(*args, **kwargs))

        return wrapper


class CollectionUtils:
    """TODO: Move out of this abstractions file if it gains more usage."""

    @staticmethod
    def filter_map(
        map: Dict[str, Any], keys: List[str], dropna=False
    ) -> Dict[str, Any]:
        """
        Returns a new dictionary with only the specified keys.
        if dropna is True, Falsey keys are droppped
        """
        filtered_map = {key: value for key, value in map.items() if key in keys}
        if not dropna:
            return filtered_map

        return {k: v for k, v in filtered_map.items() if v and not pd.isna(v)}

    @staticmethod
    def map_to_json(map: Dict) -> str:
        """Converts a map to a pretty JSON string."""
        return json.dumps(map, indent=2)

    @staticmethod
    def add_missing(map: Dict, default_map: Dict):
        """
        map: A map with some keys missing.
        default_map: A map with default values.

        Adds missing keys from default_map to map.
        """
        for key, value in default_map.items():
            if key not in map:
                map[key] = value
