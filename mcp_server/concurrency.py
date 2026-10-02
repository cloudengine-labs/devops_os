"""Concurrency control and rate limiting for MCP tool execution.

Provides a semaphore-based mechanism to limit the number of concurrent
tool executions, useful for production deployments where resource
constraints and SLA compliance are important.
"""

import asyncio
from typing import Callable, Any, TypeVar
from functools import wraps

T = TypeVar("T")


class ConcurrencyManager:
    """Manages concurrent tool execution with semaphore-based rate limiting.
    
    Limits the number of concurrent tool invocations to prevent resource
    exhaustion, enforce SLA compliance, and manage production costs.
    """

    def __init__(self, max_concurrent: int = 10):
        """Initialize concurrency manager.
        
        Args:
            max_concurrent: Maximum number of concurrent tool executions.
                          Must be between 1 and 100.
                          
        Raises:
            ValueError: If max_concurrent is outside valid range.
        """
        if not 1 <= max_concurrent <= 100:
            raise ValueError(
                f"max_concurrent must be 1-100, got {max_concurrent}"
            )
        
        self.max_concurrent = max_concurrent
        self._semaphore = asyncio.Semaphore(max_concurrent)
        self._active_calls = 0
    
    async def execute_with_limit(self, coro: Any) -> Any:
        """Execute a coroutine with concurrency limit.
        
        Acquires a slot from the semaphore before execution,
        releases it after completion.
        
        Args:
            coro: Coroutine to execute.
            
        Returns:
            Result from the coroutine.
            
        Raises:
            asyncio.TimeoutError: If operation times out.
            Any exception raised by the coroutine.
        """
        async with self._semaphore:
            self._active_calls += 1
            try:
                return await coro
            finally:
                self._active_calls -= 1
    
    def get_stats(self) -> dict[str, int]:
        """Get current concurrency statistics.
        
        Returns:
            Dictionary with keys:
            - max_concurrent: Maximum allowed concurrent calls
            - active_calls: Currently active tool executions
            - available_slots: Available semaphore slots
        """
        return {
            "max_concurrent": self.max_concurrent,
            "active_calls": self._active_calls,
            "available_slots": self.max_concurrent - self._active_calls,
        }


def with_concurrency_limit(manager: ConcurrencyManager) -> Callable:
    """Decorator to apply concurrency limiting to tool functions.
    
    Wraps a tool function to enforce concurrency limits via the manager.
    Handles both sync and async functions.
    
    Args:
        manager: ConcurrencyManager instance.
        
    Returns:
        Decorator function.
        
    Example:
        >>> manager = ConcurrencyManager(max_concurrent=5)
        >>> @with_concurrency_limit(manager)
        ... def my_tool(name: str) -> str:
        ...     return f"Processed {name}"
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        # Check if function is async
        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs) -> T:
                coro = func(*args, **kwargs)
                return await manager.execute_with_limit(coro)
            return async_wrapper
        else:
            # For sync functions, wrap with a simple tracking mechanism
            # (real concurrency limiting for sync functions requires threading)
            @wraps(func)
            def sync_wrapper(*args, **kwargs) -> T:
                # For sync functions running in thread pool, this provides
                # basic tracking but not strict limiting (FastMCP handles threading)
                manager._active_calls += 1
                try:
                    return func(*args, **kwargs)
                finally:
                    manager._active_calls -= 1
            return sync_wrapper
    
    return decorator
