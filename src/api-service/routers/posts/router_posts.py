from fastapi import APIRouter, Request, HTTPException
import grpc

from posts_client import PostsServiceClient
from config import URL_POSTS_SERVICE
from schemas import *

router = APIRouter(prefix="/post", tags=["posts"])
client = PostsServiceClient(URL_POSTS_SERVICE)

def grpc_post_to_response(grpc_post) -> PostResponse:
    return PostResponse(
        id=grpc_post.id,
        title=grpc_post.title,
        description=grpc_post.description,
        created_at=datetime.datetime.fromisoformat(grpc_post.created_at),
        updated_at=datetime.datetime.fromisoformat(grpc_post.updated_at),
        is_private=grpc_post.is_private,
        creator_id=grpc_post.creator_id,
        tags=list(grpc_post.tags)
    )

@router.post("/", response_model=PostResponse, status_code=201)
async def create_post(post: PostCreate):
    try:
        response = client.create_post(
            title=post.title,
            description=post.description,
            is_private=post.is_private,
            creator_id=post.creator_id,
            tags=post.tags
        )
        return grpc_post_to_response(response.post)
    except grpc.RpcError as e:
        raise HTTPException(
            status_code=500,
            detail=f"gRPC error: {e.details()}"
        )

@router.delete("/delete/{id}", status_code=204)
async def delete_post(post_id: int, user_id: int):
    try:
        client.delete_post(post_id=post_id, user_id=user_id)
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.NOT_FOUND:
            raise HTTPException(status_code=404, detail="Post not found")
        elif e.code() == grpc.StatusCode.PERMISSION_DENIED:
            raise HTTPException(status_code=403, detail="Permission denied")
        raise HTTPException(
            status_code=500,
            detail=f"gRPC error: {e.details()}"
        )


@router.put("/update/{id}", response_model=PostResponse)
async def update_post(post_id: int, post: PostUpdate):
    try:
        response = client.update_post(
            post_id=post_id,
            title=post.title,
            description=post.description,
            is_private=post.is_private,
            user_id=post.user_id,
            tags=post.tags
        )
        if not response.post.id:
            raise HTTPException(status_code=404, detail="Post not found")
        return grpc_post_to_response(response.post)
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.PERMISSION_DENIED:
            raise HTTPException(status_code=403, detail="Permission denied")
        raise HTTPException(
            status_code=500,
            detail=f"gRPC error: {e.details()}"
        )

@router.get("/{id}", response_model=PostResponse)
async def get_post(post_id: int, user_id: int):
    try:
        response = client.get_post(post_id=post_id, user_id=user_id)
        if not response.post.id:
            raise HTTPException(status_code=404, detail="Post not found")
        return grpc_post_to_response(response.post)
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.NOT_FOUND:
            raise HTTPException(status_code=404, detail="Post not found")
        elif e.code() == grpc.StatusCode.PERMISSION_DENIED:
            raise HTTPException(status_code=403, detail="Access denied")
        raise HTTPException(
            status_code=500,
            detail=f"gRPC error: {e.details()}"
        )


@router.get("/", response_model=PostsListResponse)
async def list_posts(page: int, page_size: int, user_id: int):
    try:
        response = client.list_posts(
            page=page,
            page_size=page_size,
            user_id=user_id
        )
        return PostsListResponse(
            posts=[grpc_post_to_response(post) for post in response.posts],
            total=response.total,
            page=response.page,
            page_size=response.page_size
        )
    except grpc.RpcError as e:
        raise HTTPException(
            status_code=500,
            detail=f"gRPC error: {e.details()}"
        )