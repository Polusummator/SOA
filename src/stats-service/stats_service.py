import grpc
from concurrent import futures

import stats_service_pb2 as pb2
import stats_service_pb2_grpc as pb2_grpc

import kafka_consumer
import threading

from database import StatsDB


class StatsService(pb2_grpc.StatsServiceServicer):
    def __init__(self, db: StatsDB):
        self.db = db

    def GetPostStats(self, request, context):
        stats = self.db.get_post_stats(request.post_id)
        return pb2.PostStatsResponse(
            post_id=request.post_id,
            views=stats["views"],
            likes=stats["likes"],
            comments=stats["comments"],
        )

    def GetPostViewsTimeline(self, request, context):
        timeline = self.db.get_post_timeline(request.post_id, "view")
        return pb2.PostTimelineResponse(
            post_id=request.post_id,
            timeline=[pb2.DayStat(date=entry["date"], count=entry["count"]) for entry in timeline]
        )

    def GetPostLikesTimeline(self, request, context):
        timeline = self.db.get_post_timeline(request.post_id, "like")
        return pb2.PostTimelineResponse(
            post_id=request.post_id,
            timeline=[pb2.DayStat(date=entry["date"], count=entry["count"]) for entry in timeline]
        )

    def GetPostCommentsTimeline(self, request, context):
        timeline = self.db.get_post_timeline(request.post_id, "comment")
        return pb2.PostTimelineResponse(
            post_id=request.post_id,
            timeline=[pb2.DayStat(date=entry["date"], count=entry["count"]) for entry in timeline]
        )

    def GetTopPosts(self, request, context):
        try:
            posts = self.db.get_top_posts(request.metric)
        except ValueError as e:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, str(e))

        return pb2.TopPostsResponse(
            posts=[pb2.PostAggregate(post_id=p["post_id"], count=p["count"]) for p in posts]
        )

    def GetTopUsers(self, request, context):
        try:
            users = self.db.get_top_users(request.metric)
        except ValueError as e:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, str(e))

        return pb2.TopUsersResponse(
            users=[pb2.UserAggregate(user_id=u["user_id"], count=u["count"]) for u in users]
        )


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pb2_grpc.add_StatsServiceServicer_to_server(StatsService(StatsDB()), server)
    server.add_insecure_port('[::]:5000')
    server.start()
    print("Server started on port 5000", flush=True)

    consumer_thread = threading.Thread(target=kafka_consumer.consume(), daemon=True)
    consumer_thread.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
