from fastapi import FastAPI, Request, Response, HTTPException
import uvicorn

from routers import router_users, router_posts

app = FastAPI()
app.include_router(router_users.router)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)