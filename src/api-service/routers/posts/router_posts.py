from fastapi import APIRouter, HTTPException, Cookie, Depends
import httpx
import grpc

from .posts_client import PostsServiceClient
from .schemas import *

from config import URL_POSTS_SERVICE, URL_USER_SERVICE

router = APIRouter(prefix="/posts", tags=["posts"])
client = PostsServiceClient(URL_POSTS_SERVICE)
user_service_client = httpx.AsyncClient(base_url=f"http://{URL_USER_SERVICE}")

async def get_current_user_id(token: str = Cookie(None)):
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        auth_response = await user_service_client.get(
            "/user/auth",
            cookies={"token": token},
            timeout=5.0
        )
        if auth_response.status_code != 200 or not auth_response.json():
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        return auth_response.json()

    except httpx.RequestError as e:
        print(str(e))
        raise HTTPException(status_code=503, detail="User Service unavailable")

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
async def create_post(post: PostBase, user_id: int = Depends(get_current_user_id)):
    try:
        response = client.create_post(
            title=post.title,
            description=post.description,
            is_private=post.is_private,
            creator_id=user_id,
            tags=post.tags
        )
        return grpc_post_to_response(response.post)
    except grpc.RpcError as e:
        raise HTTPException(
            status_code=500,
            detail=f"gRPC error: {e.details()}"
        )

@router.delete("/{post_id}", status_code=204)
async def delete_post(post_id: int, user_id: int = Depends(get_current_user_id)):
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


@router.put("/{post_id}", response_model=PostResponse)
async def update_post(post_id: int, post: PostBase, user_id: int = Depends(get_current_user_id)):
    try:
        response = client.update_post(
            post_id=post_id,
            title=post.title,
            description=post.description,
            is_private=post.is_private,
            user_id=user_id,
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

@router.get("/{post_id}", response_model=PostResponse)
async def get_post(post_id: int, user_id: int = Depends(get_current_user_id)):
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
async def list_posts(page: int, page_size: int, user_id: int = Depends(get_current_user_id)):
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