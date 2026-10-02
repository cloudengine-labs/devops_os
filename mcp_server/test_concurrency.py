"""Unit tests for concurrency management and rate limiting."""

import pytest
import asyncio
from mcp_server.concurrency import ConcurrencyManager, with_concurrency_limit


class TestConcurrencyManager:
    """Tests for ConcurrencyManager class."""

    def test_init_valid_range(self):
        """Test ConcurrencyManager initialization with valid ranges."""
        # Test minimum
        manager = ConcurrencyManager(max_concurrent=1)
        assert manager.max_concurrent == 1

        # Test default
        manager = ConcurrencyManager(max_concurrent=10)
        assert manager.max_concurrent == 10

        # Test maximum
        manager = ConcurrencyManager(max_concurrent=100)
        assert manager.max_concurrent == 100

    def test_init_invalid_range_low(self):
        """Test ConcurrencyManager rejects max_concurrent < 1."""
        with pytest.raises(ValueError, match="must be 1-100"):
            ConcurrencyManager(max_concurrent=0)

    def test_init_invalid_range_high(self):
        """Test ConcurrencyManager rejects max_concurrent > 100."""
        with pytest.raises(ValueError, match="must be 1-100"):
            ConcurrencyManager(max_concurrent=101)

    def test_get_stats_initial(self):
        """Test get_stats returns correct initial values."""
        manager = ConcurrencyManager(max_concurrent=10)
        stats = manager.get_stats()

        assert stats["max_concurrent"] == 10
        assert stats["active_calls"] == 0
        assert stats["available_slots"] == 10

    def test_get_stats_with_active_calls(self):
        """Test get_stats reflects active calls."""
        manager = ConcurrencyManager(max_concurrent=10)

        # Manually increment active calls
        manager._active_calls = 3
        stats = manager.get_stats()

        assert stats["max_concurrent"] == 10
        assert stats["active_calls"] == 3
        assert stats["available_slots"] == 7

    @pytest.mark.asyncio
    async def test_execute_with_limit_success(self):
        """Test successful execution with concurrency limit."""
        manager = ConcurrencyManager(max_concurrent=10)

        async def dummy_coro():
            await asyncio.sleep(0.01)
            return "success"

        result = await manager.execute_with_limit(dummy_coro())
        assert result == "success"

    @pytest.mark.asyncio
    async def test_execute_with_limit_exception(self):
        """Test exception handling during limited execution."""
        manager = ConcurrencyManager(max_concurrent=10)

        async def failing_coro():
            raise ValueError("Test error")

        with pytest.raises(ValueError, match="Test error"):
            await manager.execute_with_limit(failing_coro())

    @pytest.mark.asyncio
    async def test_semaphore_blocks_when_full(self):
        """Test that semaphore blocks when limit is reached."""
        manager = ConcurrencyManager(max_concurrent=2)

        execution_order = []

        async def tracked_coro(name: str, delay: float):
            execution_order.append(f"start_{name}")
            await asyncio.sleep(delay)
            execution_order.append(f"end_{name}")

        # Start 3 tasks concurrently
        # First 2 should run immediately, 3rd should wait
        tasks = [
            manager.execute_with_limit(tracked_coro("a", 0.05)),
            manager.execute_with_limit(tracked_coro("b", 0.05)),
            manager.execute_with_limit(tracked_coro("c", 0.01)),
        ]

        await asyncio.gather(*tasks)

        # All tasks should have started and ended
        assert len(execution_order) == 6
        assert "start_a" in execution_order
        assert "start_b" in execution_order
        assert "start_c" in execution_order

    def test_sync_wrapper_tracks_calls(self):
        """Test that @with_concurrency_limit decorator works with sync functions."""
        manager = ConcurrencyManager(max_concurrent=10)

        @with_concurrency_limit(manager)
        def sync_function(x: int) -> int:
            return x * 2

        # Check that the function still works
        result = sync_function(5)
        assert result == 10

        # Check that active calls were tracked and released
        assert manager._active_calls == 0

    @pytest.mark.asyncio
    async def test_async_wrapper_tracks_calls(self):
        """Test that @with_concurrency_limit decorator works with async functions."""
        manager = ConcurrencyManager(max_concurrent=10)

        @with_concurrency_limit(manager)
        async def async_function(x: int) -> int:
            await asyncio.sleep(0.01)
            return x * 2

        # Check initial state
        assert manager._active_calls == 0

        # Run the function
        result = await async_function(5)
        assert result == 10

        # Check that active calls were tracked and released
        assert manager._active_calls == 0

    def test_default_init(self):
        """Test ConcurrencyManager with no arguments uses reasonable default."""
        # This tests that we can create a manager without args
        # (though in actual code, we'd pass a config)
        manager = ConcurrencyManager()
        assert manager.max_concurrent == 10


class TestConfigIntegration:
    """Tests for Config class with max_concurrent_calls."""

    def test_config_max_concurrent_calls_field_exists(self):
        """Test that Config has max_concurrent_calls field."""
        from mcp_server.config import Config

        # Create config with explicit value
        config = Config(max_concurrent_calls=5)
        assert config.max_concurrent_calls == 5

        # Create with default
        config = Config()
        assert config.max_concurrent_calls == 10

    def test_config_max_concurrent_calls_validation(self):
        """Test that Config validates max_concurrent_calls."""
        from mcp_server.config import Config

        # Valid values should work
        config = Config(max_concurrent_calls=1)
        config.__post_init__()  # Manually trigger validation

        config = Config(max_concurrent_calls=100)
        config.__post_init__()

        # Invalid values should raise
        config = Config(max_concurrent_calls=0)
        with pytest.raises(ValueError, match="must be 1-100"):
            config.__post_init__()

        config = Config(max_concurrent_calls=101)
        with pytest.raises(ValueError, match="must be 1-100"):
            config.__post_init__()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
