from fastapi import APIRouter, Request, Response, HTTPException
import httpx

from config import URL_USER_SERVICE

router = APIRouter(prefix="/user", tags=["users"])

async def proxy_users_request(request: Request, path: str):
    url = f"{URL_USER_SERVICE}{path}"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.request(
                request.method,
                url,
                headers=dict(request.headers),
                content=await request.body(),
                params=request.query_params,
            )
            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=response.headers,
            )
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=str(e))

@router.post("/register")
async def register(request: Request):
    return await proxy_users_request(request, "/user/register")

@router.post("/login")
async def login(request: Request):
    return await proxy_users_request(request, "/user/login")

@router.get("/me/info")
async def get_me_info(request: Request):
    return await proxy_users_request(request, "/user/me/info")

@router.put("/me/info")
async def update_me_info(request: Request):
    return await proxy_users_request(request, "/user/me/info")
