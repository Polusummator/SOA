docker compose exec user-service coverage erase
docker compose exec user-service coverage run -m pytest test/test.py
docker compose exec user-service coverage report -m

docker compose exec posts-service coverage erase
docker compose exec posts-service coverage run -m pytest test/test.py
docker compose exec posts-service coverage report -m