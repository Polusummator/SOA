docker compose exec user-service coverage erase
docker compose exec user-service coverage run -m pytest test/test.py
docker compose exec user-service coverage report -m