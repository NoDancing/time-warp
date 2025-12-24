from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

import pytest

# Ensure the Django project (apps/server) is importable.
REPO_ROOT = Path(__file__).resolve().parents[1]
DJANGO_ROOT = REPO_ROOT / "apps" / "server"

if str(DJANGO_ROOT) not in sys.path:
    sys.path.insert(0, str(DJANGO_ROOT))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django  # noqa: E402

django.setup()

from rest_framework.test import APIClient  # noqa: E402


@dataclass
class _Resp:
    status_code: int
    _data: Any
    _raw: bytes

    @property
    def text(self) -> str:
        try:
            return self._raw.decode("utf-8")
        except Exception:
            return str(self._raw)

    def json(self) -> Any:
        return self._data


class ContractClient:
    """Adapter so tests can keep using client.post(..., json=...)."""

    def __init__(self) -> None:
        self._c = APIClient()

    def post(
        self, path: str, json: Optional[Dict[str, Any]] = None, **kwargs: Any
    ) -> _Resp:
        resp = self._c.post(path, data=json or {}, format="json", **kwargs)
        return _Resp(
            status_code=resp.status_code,
            _data=getattr(resp, "data", None),
            _raw=getattr(resp, "content", b""),
        )

    def get(
        self, path: str, params: Optional[Dict[str, Any]] = None, **kwargs: Any
    ) -> _Resp:
        resp = self._c.get(path, data=params or {}, format="json", **kwargs)
        return _Resp(
            status_code=resp.status_code,
            _data=getattr(resp, "data", None),
            _raw=getattr(resp, "content", b""),
        )


@pytest.fixture
def client(db) -> ContractClient:
    """Contract client with DB access enabled via pytest-django."""
    return ContractClient()
