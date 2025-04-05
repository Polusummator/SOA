# Users service

## Зона ответственности и границы:

* Регистрирует и аутентифицирует пользователей

* Хранит данные о пользователях

## Примеры запросов

```shell
curl -X POST http://localhost:5000/user/register \
     -H "Content-Type: application/json" \
     -d '{
           "username": "testuser",
           "password": "testpassword",
           "email": "test@example.com"
         }'


curl -X POST http://localhost:5000/user/login \
     -H "Content-Type: application/json" \
     -d '{
           "username": "testuser",
           "password": "testpassword",
           "email": "test@example.com"
         }'
         
         
curl -X GET http://localhost:5000/user/me/info \
     -H "Content-Type: application/json" \
     --cookie "token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InRlc3R1c2VyIiwiZXhwIjoxNzQwOTQ2NjIxLjUzNzc3NH0.ZnLMB9CtPPLCKyL_sKmY_hmfh05G9iyFYDa4F60fr6w"
     
     
curl -X PUT http://localhost:5000/user/me/info \
     -H "Content-Type: application/json" \
     --cookie "token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InRlc3R1c2VyIiwiZXhwIjoxNzQwOTQ2NjIxLjUzNzc3NH0.ZnLMB9CtPPLCKyL_sKmY_hmfh05G9iyFYDa4F60fr6w" \
     -d '{
	   "bio": "this is bio",
	   "phone_number": "+78005553535"
     }'
     
curl -X PUT http://localhost:5000/user/me/info \
     -H "Content-Type: application/json" \
     --cookie "token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InRlc3R1c2VyIiwiZXhwIjoxNzQwOTQ2NjIxLjUzNzc3NH0.ZnLMB9CtPPLCKyL_sKmY_hmfh05G9iyFYDa4F60fr6w" \
     -d '{
	   "first_name": "Aboba",
	   "birthday": "1997-01-01"
     }'
```