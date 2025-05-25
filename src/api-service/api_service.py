from fastapi import FastAPI, Request, Response, HTTPException
import uvicorn

from routers.users import router_users
from routers.posts import router_posts
from routers.stats import router_stats

app = FastAPI()
app.include_router(router_users.router)
app.include_router(router_posts.router)
app.include_router(router_stats.router)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)