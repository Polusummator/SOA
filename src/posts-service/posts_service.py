from database import PostsDB

import grpc
import posts_service_pb2
import posts_service_pb2_grpc
from concurrent import futures
import datetime

from kafka_profucer import KafkaProducer

class PostsService(posts_service_pb2_grpc.PostsServiceServicer):
    def __init__(self):
        self.db = PostsDB()
        self.kafka_producer = KafkaProducer()

    def _map_to_proto_post(self, post_data):
        return posts_service_pb2.Post(
            id=post_data["id"],
            title=post_data["title"],
            description=post_data["description"],
            created_at=post_data["created_at"].isoformat(),
            updated_at=post_data["updated_at"].isoformat(),
            is_private=post_data["is_private"],
            creator_id=post_data["creator_id"],
            tags=post_data["tags"]
        )

    def _map_to_proto_comment(self, comment_data):
        return posts_service_pb2.Comment(
            id=comment_data["id"],
            description=comment_data["description"],
            created_at=comment_data["created_at"].isoformat(),
            post_id=comment_data["post_id"],
            creator_id=comment_data["creator_id"]
        )

    def _handle_db_error(self, context, e):
        context.set_code(grpc.StatusCode.INTERNAL)
        context.set_details(f"Database error: {str(e)}")
        return None

    def CreatePost(self, request, context):
        try:
            post_data = self.db.create_post(
                title=request.title,
                description=request.description,
                creator_id=request.creator_id,
                is_private=request.is_private,
                tags=request.tags
            )

            event = {
                "event_type": "post_created",
                "post_id": post_data["id"],
                "creator_id": post_data["creator_id"],
                "created_at": post_data["created_at"].isoformat(),
                "metadata": {
                    "is_private": post_data["is_private"]
                }
            }
            self.kafka_producer.produce(
                topic="post-events",
                key=str(post_data["id"]),
                value=event
            )

            return posts_service_pb2.CreatePostResponse(
                post=self._map_to_proto_post(post_data)
            )
        except Exception as e:
            self._handle_db_error(context, e)
            return posts_service_pb2.CreatePostResponse()

    def DeletePost(self, request, context):
        try:
            success = self.db.delete_post(request.id, request.user_id)
            if not success:
                context.set_code(grpc.StatusCode.PERMISSION_DENIED)
                context.set_details("Permission denied or post not found")
            return posts_service_pb2.DeletePostResponse()
        except Exception as e:
            self._handle_db_error(context, e)
            return posts_service_pb2.DeletePostResponse()

    def UpdatePost(self, request, context):
        try:
            post_data = self.db.update_post(
                post_id=request.id,
                title=request.title,
                description=request.description,
                is_private=request.is_private,
                user_id=request.user_id,
                tags=request.tags
            )
            if not post_data:
                context.set_code(grpc.StatusCode.PERMISSION_DENIED)
                context.set_details("Permission denied or post not found")
                return posts_service_pb2.UpdatePostResponse()

            return posts_service_pb2.UpdatePostResponse(
                post=self._map_to_proto_post(post_data)
            )
        except Exception as e:
            self._handle_db_error(context, e)
            return posts_service_pb2.UpdatePostResponse()

    def GetPost(self, request, context):
        try:
            post_data = self.db.get_post(request.id, request.user_id)
            if not post_data:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Post not found or access denied")
                return posts_service_pb2.GetPostResponse()

            event = {
                "event_type": "post_viewed",
                "user_id": request.user_id,
                "post_id": request.id,
                "timestamp": datetime.datetime.now().isoformat()
            }
            self.kafka_producer.produce(
                topic="post-interactions",
                key=f"{request.user_id}-{request.id}",
                value=event
            )

            return posts_service_pb2.GetPostResponse(
                post=self._map_to_proto_post(post_data)
            )
        except Exception as e:
            self._handle_db_error(context, e)
            return posts_service_pb2.GetPostResponse()

    def ListPosts(self, request, context):
        try:
            result = self.db.list_posts(
                page=request.page,
                page_size=request.page_size,
                user_id=request.user_id
            )
            return posts_service_pb2.ListPostsResponse(
                posts=[self._map_to_proto_post(post) for post in result["posts"]],
                total=result["total"],
                page=result["page"],
                page_size=result["page_size"]
            )
        except Exception as e:
            self._handle_db_error(context, e)
            return posts_service_pb2.ListPostsResponse()

    def CommentPost(self, request, context):
        try:
            if not self.db.can_access_post(request.post_id, request.creator_id):
                context.set_code(grpc.StatusCode.PERMISSION_DENIED)
                context.set_details("No access to this post")
                return posts_service_pb2.CommentPostResponse()

            comment_data = self.db.create_comment(
                description=request.description,
                post_id=request.post_id,
                creator_id=request.creator_id
            )

            event = {
                "event_type": "post_commented",
                "user_id": request.creator_id,
                "post_id": request.post_id,
                "comment_id": comment_data["id"],
                "timestamp": datetime.datetime.now().isoformat()
            }
            self.kafka_producer.produce(
                topic="post-interactions",
                key=f"{request.creator_id}-{request.post_id}",
                value=event
            )

            return posts_service_pb2.CommentPostResponse(
                comment=self._map_to_proto_comment(comment_data)
            )
        except Exception as e:
            self._handle_db_error(context, e)
            return posts_service_pb2.CommentPostResponse()

    def ListComments(self, request, context):
        try:
            result = self.db.list_comments(
                post_id=request.post_id,
                user_id=request.user_id,
                page=request.page,
                page_size=request.page_size
            )

            if result is None:
                context.set_code(grpc.StatusCode.PERMISSION_DENIED)
                context.set_details("No access to this post or post not found")
                return posts_service_pb2.ListCommentsResponse()

            return posts_service_pb2.ListCommentsResponse(
                comments=[self._map_to_proto_comment(comment) for comment in result["comments"]],
                total=result["total"],
                page=result["page"],
                page_size=result["page_size"]
            )
        except Exception as e:
            self._handle_db_error(context, e)
            return posts_service_pb2.ListCommentsResponse()

    def LikePost(self, request, context):
        try:
            if not self.db.can_access_post(request.post_id, request.user_id):
                context.set_code(grpc.StatusCode.PERMISSION_DENIED)
                context.set_details("No access to this post")
                return posts_service_pb2.LikePostResponse()

            event = {
                "event_type": "post_liked",
                "user_id": request.user_id,
                "post_id": request.post_id,
                "timestamp": datetime.datetime.now().isoformat()
            }
            self.kafka_producer.produce(
                topic="post-interactions",
                key=f"{request.user_id}-{request.post_id}",
                value=event
            )

            return posts_service_pb2.LikePostResponse()
        except Exception as e:
            self._handle_db_error(context, e)
            return posts_service_pb2.LikePostResponse()

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    posts_service_pb2_grpc.add_PostsServiceServicer_to_server(PostsService(), server)
    server.add_insecure_port('[::]:5000')
    server.start()
    print("Server started on port 5000", flush=True)
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
