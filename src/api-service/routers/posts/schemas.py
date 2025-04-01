from pydantic import BaseModel
from typing import List, Optional
import datetime

class PostBase(BaseModel):
    title: str
    description: str
    is_private: bool = False
    tags: List[str] = []

class PostCreate(PostBase):
    creator_id: int

class PostUpdate(PostBase):
    user_id: int

class PostResponse(PostBase):
    id: int
    creator_id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime

class PostsListResponse(BaseModel):
    posts: List[PostResponse]
    total: int
    page: int
    page_size: int