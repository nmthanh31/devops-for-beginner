from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient
from redis.asyncio import Redis
from redis.exceptions import RedisError

from kubernetes_alert_gateway.api.dependencies import get_redis_client
from kubernetes_alert_gateway.main import app

client = TestClient(app=app)


@pytest.fixture
def fake_redis_client():
    redis_client = MagicMock(spec=Redis)

    # redis-py không khai báo ping theo cách unittest.mock tự nhận diện
    # chắc chắn là async, nên ta gán AsyncMock rõ ràng cho phương thức này.
    redis_client.ping = AsyncMock()

    app.dependency_overrides[get_redis_client] = (
        lambda: redis_client
    )

    yield redis_client

    app.dependency_overrides.pop(get_redis_client, None)


def test_liveness_returns_200():
    response = client.get("/health/live")

    assert response.status_code == 200
    assert response.json() == {"status": "alive"}


def test_readiness_returns_200(fake_redis_client):
    fake_redis_client.ping.return_value = True
    response = client.get("/health/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ready"}
    fake_redis_client.ping.assert_awaited_once_with()


def test_readiness_returns_503_when_redis_fails(
    fake_redis_client,
):
    fake_redis_client.ping.side_effect = RedisError("fake Redis failure")
    response = client.get("/health/ready")

    assert response.status_code == 503
    assert response.json() == {"detail": "Redis unavailable"}
    fake_redis_client.ping.assert_awaited_once_with()
