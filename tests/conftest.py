"""Isolate unit tests before application imports can initialize external services."""

import socket
from unittest.mock import Mock

import pytest


def pytest_configure(config):
    isolation = pytest.MonkeyPatch()
    config.add_cleanup(isolation.undo)
    isolation.setenv("DATABASE_URL", "sqlite:///:memory:")
    isolation.setenv("OPENAI_API_KEY", "unit-test-placeholder")
    isolation.setenv("OPENAI_BASE_URL", "http://127.0.0.1:9/v1")
    isolation.setenv("ANONYMIZED_TELEMETRY", "False")

    # Prevent local .env files from restoring real credentials, even with override=True.
    isolation.setattr("dotenv.load_dotenv", lambda *args, **kwargs: False)

    def reject_network(*args, **kwargs):
        raise AssertionError("Unit tests must mock external network calls")

    # Windows asyncio uses loopback socket pairs internally. Permit only those
    # addresses; database connections still use the in-memory SQLite engine.
    def guarded_connect(original):
        def connect(sock, address):
            if isinstance(address, tuple) and address[0] in ("127.0.0.1", "::1"):
                return original(sock, address)
            return reject_network()

        return connect

    isolation.setattr(socket.socket, "connect", guarded_connect(socket.socket.connect))
    isolation.setattr(
        socket.socket, "connect_ex", guarded_connect(socket.socket.connect_ex)
    )

    # tools.py creates this at import time; never initialize persistent Chroma or
    # generate OpenAI embeddings during collection. Tests must mock retrieval.
    from app.domains.chat import vector_store

    store = Mock(spec=vector_store.ChocolateShopVectorStore)
    for method in ("query_faqs", "query_inventories", "filter_products_by_price"):
        getattr(store, method).side_effect = reject_network
    isolation.setattr(vector_store, "ChocolateShopVectorStore", lambda: store)
