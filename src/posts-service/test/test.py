import pytest
from database import PostsDB
from posts_service import PostsService
import posts_service_pb2
import posts_service_pb2_grpc
from grpc import StatusCode
from unittest.mock import MagicMock

@pytest.fixture(scope="function")
def posts_service():
    db = PostsDB()
    db.delete_all_posts()
    service = PostsService()
    service.db = db
    return service

@pytest.fixture(scope="function")
def context():
    return MagicMock()

def test_create_post(posts_service):
    request = posts_service_pb2.CreatePostRequest(
        title="Test Post",
        description="This is a test post",
        creator_id=1,
        is_private=False,
        tags=["test", "post"]
    )
    context = MagicMock()
    response = posts_service.CreatePost(request, context)
    assert response.post.title == "Test Post"
    assert response.post.description == "This is a test post"
    assert response.post.creator_id == 1
    assert response.post.is_private is False
    assert response.post.tags == ["test", "post"]

def test_delete_post(posts_service):
    create_request = posts_service_pb2.CreatePostRequest(
        title="Test Post",
        description="This is a test post",
        creator_id=1,
        is_private=False,
        tags=["test", "post"]
    )
    context = MagicMock()
    create_response = posts_service.CreatePost(create_request, context)
    post_id = create_response.post.id

    delete_request = posts_service_pb2.DeletePostRequest(id=post_id, user_id=1)
    delete_response = posts_service.DeletePost(delete_request, context)
    assert context.set_code.call_count == 0

def test_update_post(posts_service):
    create_request = posts_service_pb2.CreatePostRequest(
        title="Test Post",
        description="This is a test post",
        creator_id=1,
        is_private=False,
        tags=["test", "post"]
    )
    context = MagicMock()
    create_response = posts_service.CreatePost(create_request, context)
    post_id = create_response.post.id

    update_request = posts_service_pb2.UpdatePostRequest(
        id=post_id,
        title="Updated Post",
        description="This is an updated test post",
        is_private=True,
        user_id=1,
        tags=["updated", "post"]
    )
    update_response = posts_service.UpdatePost(update_request, context)
    assert update_response.post.title == "Updated Post"
    assert update_response.post.description == "This is an updated test post"
    assert update_response.post.is_private is True
    assert update_response.post.tags == ["updated", "post"]

def test_get_post(posts_service):
    create_request = posts_service_pb2.CreatePostRequest(
        title="Test Post",
        description="This is a test post",
        creator_id=1,
        is_private=False,
        tags=["test", "post"]
    )
    context = MagicMock()
    create_response = posts_service.CreatePost(create_request, context)
    post_id = create_response.post.id

    get_request = posts_service_pb2.GetPostRequest(id=post_id, user_id=1)
    get_response = posts_service.GetPost(get_request, context)
    assert get_response.post.title == "Test Post"
    assert get_response.post.description == "This is a test post"
    assert get_response.post.creator_id == 1
    assert get_response.post.is_private is False
    assert get_response.post.tags == ["test", "post"]

def test_get_nonexistent_post(posts_service, context):
    get_request = posts_service_pb2.GetPostRequest(id=999, user_id=1)
    get_response = posts_service.GetPost(get_request, context)
    assert context.set_code.call_count == 1
    assert context.set_code.call_args[0][0] == StatusCode.NOT_FOUND

def test_list_posts(posts_service):
    create_request = posts_service_pb2.CreatePostRequest(
        title="Test Post",
        description="This is a test post",
        creator_id=1,
        is_private=False,
        tags=["test", "post"]
    )
    context = MagicMock()
    posts_service.CreatePost(create_request, context)

    list_request = posts_service_pb2.ListPostsRequest(page=1, page_size=10, user_id=1)
    list_response = posts_service.ListPosts(list_request, context)
    assert len(list_response.posts) == 1
    assert list_response.total == 1
    assert list_response.page == 1
    assert list_response.page_size == 10

def test_list_posts_with_pagination(posts_service, context):
    for i in range(15):
        create_request = posts_service_pb2.CreatePostRequest(
            title=f"Test Post {i}",
            description="This is a test post",
            creator_id=1,
            is_private=False,
            tags=["test", "post"]
        )
        posts_service.CreatePost(create_request, context)

    list_request = posts_service_pb2.ListPostsRequest(page=2, page_size=10, user_id=1)
    list_response = posts_service.ListPosts(list_request, context)
    assert len(list_response.posts) == 5
    assert list_response.total == 15
    assert list_response.page == 2
    assert list_response.page_size == 10

# Wrong user tests

def test_get_private_post_with_wrong_user(posts_service, context):
    create_request = posts_service_pb2.CreatePostRequest(
        title="Private Post",
        description="This is a private post",
        creator_id=1,
        is_private=True,
        tags=["private", "post"]
    )
    create_response = posts_service.CreatePost(create_request, context)
    post_id = create_response.post.id

    get_request = posts_service_pb2.GetPostRequest(id=post_id, user_id=2)
    get_response = posts_service.GetPost(get_request, context)
    context.set_code.assert_called_with(StatusCode.NOT_FOUND)

def test_delete_post_with_wrong_user(posts_service, context):
    create_request = posts_service_pb2.CreatePostRequest(
        title="Test Post",
        description="This is a test post",
        creator_id=1,
        is_private=False,
        tags=["test", "post"]
    )
    create_response = posts_service.CreatePost(create_request, context)
    post_id = create_response.post.id

    delete_request = posts_service_pb2.DeletePostRequest(id=post_id, user_id=2)
    delete_response = posts_service.DeletePost(delete_request, context)
    assert context.set_code.call_count == 1
    assert context.set_code.call_args[0][0] == StatusCode.PERMISSION_DENIED

def test_update_post_with_wrong_user(posts_service, context):
    create_request = posts_service_pb2.CreatePostRequest(
        title="Test Post",
        description="This is a test post",
        creator_id=1,
        is_private=False,
        tags=["test", "post"]
    )
    create_response = posts_service.CreatePost(create_request, context)
    post_id = create_response.post.id

    update_request = posts_service_pb2.UpdatePostRequest(
        id=post_id,
        title="Updated Post",
        description="This is an updated test post",
        is_private=True,
        user_id=2,
        tags=["updated", "post"]
    )
    update_response = posts_service.UpdatePost(update_request, context)
    assert context.set_code.call_count == 1
    assert context.set_code.call_args[0][0] == StatusCode.PERMISSION_DENIED