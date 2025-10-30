import pytest


@pytest.mark.asyncio
async def simple_test() -> None:
    """Simple test to debug pytest-asyncio issue."""
    assert True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
