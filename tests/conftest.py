import os

import pytest


@pytest.fixture(scope="session")
def base_url() -> str:
    """
    Base URL for the running API under test.

    Usage:
      TIME_WARP_API_BASE_URL=http://localhost:3000 pytest
    """
    return os.environ.get("TIME_WARP_API_BASE_URL", "http://localhost:3000").rstrip("/")