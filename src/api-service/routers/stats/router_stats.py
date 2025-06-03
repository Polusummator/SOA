from fastapi import APIRouter, Depends, HTTPException
from .stats_client import StatsServiceClient
from .schemas import *
from config import URL_STATS_SERVICE
import grpc

router = APIRouter(prefix="/stats", tags=["stats"])
client = StatsServiceClient(URL_STATS_SERVICE)

@router.get("/post/{post_id}", response_model=PostStats)
async def get_post_stats(post_id: int):
    try:
        response = client.get_post_stats(post_id)
        return PostStats(
            post_id=response.post_id,
            views=response.views,
            likes=response.likes,
            comments=response.comments
        )
    except grpc.RpcError as e:
        raise HTTPException(status_code=500, detail=f"gRPC error: {e.details()}")

@router.get("/post/{post_id}/dynamics", response_model=PostDynamics)
async def get_post_dynamics(post_id: int):
    try:
        views = client.get_post_timeline(post_id, "view").timeline
        likes = client.get_post_timeline(post_id, "like").timeline
        comments = client.get_post_timeline(post_id, "comment").timeline

        timeline = {}
        for stat in views:
            timeline[stat.date] = {"timestamp": stat.date, "views": stat.count, "likes": 0, "comments": 0}
        for stat in likes:
            timeline.setdefault(stat.date, {"timestamp": stat.date, "views": 0, "likes": 0, "comments": 0})
            timeline[stat.date]["likes"] = stat.count
        for stat in comments:
            timeline.setdefault(stat.date, {"timestamp": stat.date, "views": 0, "likes": 0, "comments": 0})
            timeline[stat.date]["comments"] = stat.count

        sorted_data = sorted(timeline.values(), key=lambda x: x["timestamp"])
        return PostDynamics(
            post_id=post_id,
            data=[
                TimePointStats(
                    timestamp=date,
                    views=entry["views"],
                    likes=entry["likes"],
                    comments=entry["comments"]
                ) for date, entry in zip(timeline.keys(), sorted_data)
            ]
        )
    except grpc.RpcError as e:
        raise HTTPException(status_code=500, detail=f"gRPC error: {e.details()}")

@router.get("/top/posts", response_model=TopPostsResponse)
async def get_top_posts(metric: str = "post_viewed"):
    try:
        response = client.get_top_posts(metric)
        return TopPostsResponse(posts=[
            TopPost(post_id=p.post_id, score=p.count) for p in response.posts
        ])
    except grpc.RpcError as e:
        raise HTTPException(status_code=500, detail=f"gRPC error: {e.details()}")

@router.get("/top/users", response_model=TopUsersResponse)
async def get_top_users(metric: str = "post_viewed"):
    try:
        response = client.get_top_users(metric)
        return TopUsersResponse(users=[
            TopUser(user_id=u.user_id, score=u.count) for u in response.users
        ])
    except grpc.RpcError as e:
        raise HTTPException(status_code=500, detail=f"gRPC error: {e.details()}")
