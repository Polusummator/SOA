from fastapi import FastAPI, Request, Response, HTTPException
import uvicorn
import httpx

URL_USER_SERVICE = "http://user-service:5000"

app = FastAPI()

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT"])
async def user(path: str, request: Request):
    url = f"{URL_USER_SERVICE}/{path}"
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


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)