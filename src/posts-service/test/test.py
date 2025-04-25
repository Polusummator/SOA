import pytest
from database import *
from posts_service import PostsService
import posts_service_pb2
import posts_service_pb2_grpc
from grpc import StatusCode
from unittest.mock import MagicMock

@pytest.fixture(scope="function")
def posts_service():
    db = PostsDB()
    with db.Session() as session:
        session.query(Comment).delete()
        session.query(PostTag).delete()
        session.query(Post).delete()
        session.commit()
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

def test_get_post_with_invalid_id(posts_service, context):
    get_request = posts_service_pb2.GetPostRequest(id=999, user_id=1)
    get_response = posts_service.GetPost(get_request, context)
    assert context.set_code.call_count == 1
    assert context.set_code.call_args[0][0] == StatusCode.NOT_FOUND

def test_update_post_with_invalid_id(posts_service, context):
    update_request = posts_service_pb2.UpdatePostRequest(
        id=999,
        title="Updated Post",
        description="This is an updated test post",
        is_private=True,
        user_id=1,
        tags=["updated", "post"]
    )
    update_response = posts_service.UpdatePost(update_request, context)
    assert context.set_code.call_count == 1
    assert context.set_code.call_args[0][0] == StatusCode.PERMISSION_DENIED

def test_delete_post_with_invalid_id(posts_service, context):
    delete_request = posts_service_pb2.DeletePostRequest(id=999, user_id=1)
    delete_response = posts_service.DeletePost(delete_request, context)
    assert context.set_code.call_count == 1
    assert context.set_code.call_args[0][0] == StatusCode.PERMISSION_DENIED

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


def test_comment_post(posts_service, context):
    create_request = posts_service_pb2.CreatePostRequest(
        title="Test Post",
        description="Test content",
        creator_id=1,
        is_private=False,
        tags=["test"]
    )
    post = posts_service.CreatePost(create_request, context).post

    comment_request = posts_service_pb2.CommentPostRequest(
        description="Great post!",
        post_id=post.id,
        creator_id=2
    )
    response = posts_service.CommentPost(comment_request, context)

    assert response.comment.description == "Great post!"
    assert response.comment.post_id == post.id
    assert response.comment.creator_id == 2
    assert context.set_code.call_count == 0


def test_comment_nonexistent_post(posts_service, context):
    comment_request = posts_service_pb2.CommentPostRequest(
        description="Test comment",
        post_id=999,
        creator_id=1
    )
    response = posts_service.CommentPost(comment_request, context)

    assert context.set_code.call_count == 1
    assert context.set_code.call_args[0][0] == StatusCode.PERMISSION_DENIED


def test_list_comments(posts_service, context):
    post_request = posts_service_pb2.CreatePostRequest(
        title="Post with comments",
        description="Content",
        creator_id=1,
        is_private=False,
        tags=[]
    )
    post = posts_service.CreatePost(post_request, context).post

    for i in range(3):
        comment_request = posts_service_pb2.CommentPostRequest(
            description=f"Comment {i}",
            post_id=post.id,
            creator_id=i + 1
        )
        posts_service.CommentPost(comment_request, context)

    list_request = posts_service_pb2.ListCommentsRequest(
        post_id=post.id,
        page=1,
        page_size=10,
        user_id=1
    )
    response = posts_service.ListComments(list_request, context)

    assert len(response.comments) == 3
    assert response.total == 3
    assert response.page == 1
    assert response.page_size == 10


def test_list_comments_pagination(posts_service, context):
    post_request = posts_service_pb2.CreatePostRequest(
        title="Post for pagination",
        description="Content",
        creator_id=1,
        is_private=False,
        tags=[]
    )
    post = posts_service.CreatePost(post_request, context).post

    for i in range(15):
        comment_request = posts_service_pb2.CommentPostRequest(
            description=f"Comment {i}",
            post_id=post.id,
            creator_id=1
        )
        posts_service.CommentPost(comment_request, context)

    list_request = posts_service_pb2.ListCommentsRequest(
        post_id=post.id,
        page=2,
        page_size=10,
        user_id=1
    )
    response = posts_service.ListComments(list_request, context)

    assert len(response.comments) == 5
    assert response.total == 15
    assert response.page == 2
    assert response.page_size == 10


def test_list_comments_private_post(posts_service, context):
    post_request = posts_service_pb2.CreatePostRequest(
        title="Private post",
        description="Secret content",
        creator_id=1,
        is_private=True,
        tags=[]
    )
    post = posts_service.CreatePost(post_request, context).post

    comment_request = posts_service_pb2.CommentPostRequest(
        description="My comment",
        post_id=post.id,
        creator_id=1
    )
    posts_service.CommentPost(comment_request, context)

    list_request = posts_service_pb2.ListCommentsRequest(
        post_id=post.id,
        page=1,
        page_size=10,
        user_id=2
    )
    response = posts_service.ListComments(list_request, context)

    assert len(response.comments) == 0
    assert response.total == 0


def test_like_post(posts_service, context):
    post_request = posts_service_pb2.CreatePostRequest(
        title="Post to like",
        description="Content",
        creator_id=1,
        is_private=False,
        tags=[]
    )
    post = posts_service.CreatePost(post_request, context).post

    like_request = posts_service_pb2.LikePostRequest(
        user_id=2,
        post_id=post.id
    )
    response = posts_service.LikePost(like_request, context)

    assert context.set_code.call_count == 0


def test_like_nonexistent_post(posts_service, context):
    like_request = posts_service_pb2.LikePostRequest(
        user_id=1,
        post_id=999
    )
    response = posts_service.LikePost(like_request, context)

    assert context.set_code.call_count == 1
    assert context.set_code.call_args[0][0] == StatusCode.PERMISSION_DENIED


def test_like_private_post(posts_service, context):
    post_request = posts_service_pb2.CreatePostRequest(
        title="Private post",
        description="Secret content",
        creator_id=1,
        is_private=True,
        tags=[]
    )
    post = posts_service.CreatePost(post_request, context).post

    like_request = posts_service_pb2.LikePostRequest(
        user_id=2,
        post_id=post.id
    )
    response = posts_service.LikePost(like_request, context)

    assert context.set_code.call_count == 1
    assert context.set_code.call_args[0][0] == StatusCode.PERMISSION_DENIED
