from typing import Any, Dict, Callable, TypeVar, Protocol, overload

T = TypeVar('T', bound=Dict[str, Any])

class NougatDict(Protocol):
    def get(self, key: str, default: Any = ...) -> Any: ...
    def nougat(self, *keys: str, default: Any = None) -> Any: ...

def nougat(self: Dict[str, Any], *keys: str, default: Any = None) -> Any: ...
def initNougat(obj: T) -> T & NougatDict: ...
