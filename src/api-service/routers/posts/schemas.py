from pydantic import BaseModel
from typing import List
import datetime

class PostBase(BaseModel):
    title: str
    description: str
    is_private: bool = False
    tags: List[str] = []

class PostResponse(PostBase):
    id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime
    creator_id: int

class PostsListResponse(BaseModel):
    posts: List[PostResponse]
    total: int
    page: int
    page_size: int

class CommentBase(BaseModel):
    description: str

class CommentResponse(CommentBase):
    id: int
    created_at: datetime.datetime
    post_id: int
    creator_id: int

class CommentsListResponse(BaseModel):
    comments: List[CommentResponse]
    total: int
    page: int
    page_size: int

class LikeResponse(BaseModel):
    success: bool