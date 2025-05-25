import grpc
import stats_service_pb2 as pb2
import stats_service_pb2_grpc as pb2_grpc


class StatsServiceClient:
    def __init__(self, host: str):
        self.channel = grpc.insecure_channel(host)
        self.stub = pb2_grpc.StatsServiceStub(self.channel)

    def get_post_stats(self, post_id: int):
        return self.stub.GetPostStats(pb2.PostRequest(post_id=post_id))

    def get_post_timeline(self, post_id: int, metric: str):
        request = pb2.PostRequest(post_id=post_id)
        if metric == "view":
            return self.stub.GetPostViewsTimeline(request)
        elif metric == "like":
            return self.stub.GetPostLikesTimeline(request)
        elif metric == "comment":
            return self.stub.GetPostCommentsTimeline(request)
        else:
            raise ValueError("Unknown metric")

    def get_top_posts(self, metric: str):
        return self.stub.GetTopPosts(pb2.TopRequest(metric=metric))

    def get_top_users(self, metric: str):
        return self.stub.GetTopUsers(pb2.TopRequest(metric=metric))
