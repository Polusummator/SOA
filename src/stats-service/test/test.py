import pytest
from unittest.mock import MagicMock
import grpc

import stats_service_pb2 as pb2
from stats_service import StatsService


@pytest.fixture
def mock_db():
    return MagicMock()

@pytest.fixture
def context():
    ctx = MagicMock()
    ctx.abort.side_effect = grpc.RpcError("Invalid metric")
    return ctx

@pytest.fixture
def stats_service(mock_db):
    return StatsService(db=mock_db), mock_db


def test_get_post_stats(stats_service):
    service, db = stats_service
    db.get_post_stats.return_value = {"views": 100, "likes": 50, "comments": 20}

    request = pb2.PostRequest(post_id=1)
    response = service.GetPostStats(request, None)

    assert response.post_id == 1
    assert response.views == 100
    assert response.likes == 50
    assert response.comments == 20


def test_get_post_stats_no_data(stats_service):
    service, db = stats_service
    db.get_post_stats.return_value = {"views": 0, "likes": 0, "comments": 0}

    request = pb2.PostRequest(post_id=2)
    response = service.GetPostStats(request, None)

    assert response.post_id == 2
    assert response.views == 0
    assert response.likes == 0
    assert response.comments == 0


def test_get_post_timeline_valid_metric(stats_service):
    service, db = stats_service
    db.get_post_timeline.return_value = [
        {"date": "2024-01-01", "count": 5},
        {"date": "2024-01-02", "count": 10}
    ]

    request = pb2.PostRequest(post_id=42)
    response = service.GetPostViewsTimeline(request, None)

    assert response.post_id == 42
    assert len(response.timeline) == 2
    assert response.timeline[0].date == "2024-01-01"
    assert response.timeline[0].count == 5


def test_get_top_posts(stats_service):
    service, db = stats_service
    db.get_top_posts.return_value = [
        {"post_id": 1, "count": 30},
        {"post_id": 2, "count": 20}
    ]

    request = pb2.TopRequest(metric="post_viewed")
    response = service.GetTopPosts(request, None)

    assert len(response.posts) == 2
    assert response.posts[0].post_id == 1
    assert response.posts[0].count == 30


def test_get_top_posts_invalid_metric(stats_service, context):
    service, db = stats_service
    request = pb2.TopRequest(metric="invalid")
    db.get_top_posts.side_effect = ValueError("Invalid metric")

    with pytest.raises(grpc.RpcError):
        service.GetTopPosts(request, context)

    context.abort.assert_called_once_with(grpc.StatusCode.INVALID_ARGUMENT, "Invalid metric")



def test_get_top_users(stats_service):
    service, db = stats_service
    db.get_top_users.return_value = [
        {"user_id": 1, "count": 100},
        {"user_id": 2, "count": 80}
    ]

    request = pb2.TopRequest(metric="post_liked")
    response = service.GetTopUsers(request, None)

    assert len(response.users) == 2
    assert response.users[0].user_id == 1
    assert response.users[0].count == 100


def test_get_top_users_invalid_metric(stats_service, context):
    service, db = stats_service
    request = pb2.TopRequest(metric="invalid")
    db.get_top_users.side_effect = ValueError("Invalid metric")

    with pytest.raises(grpc.RpcError):
        service.GetTopUsers(request, context)

    context.abort.assert_called_once_with(grpc.StatusCode.INVALID_ARGUMENT, "Invalid metric")

