import grpc
import posts_service_pb2
import posts_service_pb2_grpc

class PostsServiceClient:
    def __init__(self, host):
        self.channel = grpc.insecure_channel(host)
        self.stub = posts_service_pb2_grpc.PostsServiceStub(self.channel)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.channel.close()

    def create_post(self, title, description, is_private, creator_id, tags):
        request = posts_service_pb2.CreatePostRequest(
            title=title,
            description=description,
            is_private=is_private,
            creator_id=creator_id,
            tags=tags
        )
        return self.stub.CreatePost(request)

    def delete_post(self, post_id, user_id):
        request = posts_service_pb2.DeletePostRequest(
            id=post_id,
            user_id=user_id
        )
        return self.stub.DeletePost(request)

    def update_post(self, post_id, title, description, is_private, user_id, tags):
        request = posts_service_pb2.UpdatePostRequest(
            id=post_id,
            title=title,
            description=description,
            is_private=is_private,
            user_id=user_id,
            tags=tags
        )
        return self.stub.UpdatePost(request)

    def get_post(self, post_id, user_id):
        request = posts_service_pb2.GetPostRequest(
            id=post_id,
            user_id=user_id
        )
        return self.stub.GetPost(request)

    def list_posts(self, page, page_size, user_id=None):
        request = posts_service_pb2.ListPostsRequest(
            page=page,
            page_size=page_size,
            user_id=user_id
        )
        return self.stub.ListPosts(request)

    def comment_post(self, description, post_id, creator_id):
        request = posts_service_pb2.CommentPostRequest(
            description=description,
            post_id=post_id,
            creator_id=creator_id
        )
        return self.stub.CommentPost(request)

    def list_comments(self, page, page_size, user_id, post_id):
        request = posts_service_pb2.ListCommentsRequest(
            page=page,
            page_size=page_size,
            user_id=user_id,
            post_id=post_id
        )
        return self.stub.ListComments(request)


    def like_post(self, user_id, post_id):
        request = posts_service_pb2.LikePostRequest(
            user_id=user_id,
            post_id=post_id
        )
        return self.stub.LikePost(request)
