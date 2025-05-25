from pydantic import BaseModel
from typing import List, Union
from datetime import date


class PostStats(BaseModel):
    post_id: int
    views: int
    likes: int
    comments: int


class TimePointStats(BaseModel):
    timestamp: Union[str, date]
    views: int
    likes: int
    comments: int


class PostDynamics(BaseModel):
    post_id: int
    data: List[TimePointStats]


class TopPost(BaseModel):
    post_id: int
    score: int


class TopUser(BaseModel):
    user_id: int
    score: int


class TopPostsResponse(BaseModel):
    posts: List[TopPost]


class TopUsersResponse(BaseModel):
    users: List[TopUser]
