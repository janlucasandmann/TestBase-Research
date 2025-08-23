"""Cache interface for future file-based caching."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Optional


class CacheInterface(ABC):
    """Abstract base class for cache implementations."""
    
    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """Retrieve value from cache."""
        pass
    
    @abstractmethod
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Store value in cache."""
        pass
    
    @abstractmethod
    def delete(self, key: str) -> None:
        """Remove value from cache."""
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """Clear all cache entries."""
        pass


class NoOpCache(CacheInterface):
    """No-operation cache implementation (MVP)."""
    
    def get(self, key: str) -> Optional[Any]:
        """Always returns None."""
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Does nothing."""
        pass
    
    def delete(self, key: str) -> None:
        """Does nothing."""
        pass
    
    def clear(self) -> None:
        """Does nothing."""
        pass


cache = NoOpCache()