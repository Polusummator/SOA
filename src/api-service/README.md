# API service

## Зона ответственности и границы:

* Направляет запросы от пользователя (поступающие через UI) в другие сервисы

* Не хранит данные, нужен только для маршрутизации

## Примеры запросов:

```shell
# Регистрация пользователя
curl -X POST "http://localhost:8000/user/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "Testpass123!",
    "email": "test@example.com"
  }'

# Логин (выдаёт куки)
curl -c cookies.txt -X POST "http://localhost:8000/user/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "Testpass123!",
    "email": "test@example.com"
  }'
```

```shell
# Создание поста
curl -b cookies.txt -X POST "http://localhost:8000/posts/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My first post",
    "description": "This is a test post",
    "is_private": false,
    "tags": ["test", "demo"]
  }'
  
# Обновление поста
curl -b cookies.txt -X PUT "http://localhost:8000/posts/1" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated title",
    "description": "Updated content",
    "is_private": true,
    "tags": ["updated"]
  }'
  
# Получение пагинированного списка постов
curl -b cookies.txt -X GET "http://localhost:8000/posts/?page=1&page_size=10"

# Получение одного поста
curl -b cookies.txt -X GET "http://localhost:8000/posts/1"
```

```shell
# Получение поста без аутентификации
curl -X GET "http://localhost:8000/posts/1"
```

```shell
# Попытка обновить чужой пост
curl -X POST "http://localhost:8000/user/register" \
  -H "Content-Type: application/json" \
  -d '{"username": "hacker", "password": "Hack123!", "email": "hack@example.com"}'

curl -c hacker_cookies.txt -X POST "http://localhost:8000/user/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "hacker", "password": "Hack123!", "email": "hack@example.com"}'

curl -b hacker_cookies.txt -X PUT "http://localhost:8000/posts/1" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Hacked Title",
    "description": "Hacked Description",
    "is_private": false,
    "tags": ["hacked"]
  }'
```

```shell
# Создание приватного поста
curl -b cookies.txt -X POST "http://localhost:8000/posts/" \
  -H "Content-Type: application/json" \
  -d '{"title": "Private", "description": "aboba", "is_private": true}'

# Он не виден другому пользователю
curl -b hacker_cookies.txt -X GET "http://localhost:8000/posts/2"

# Виден создателю
curl -b cookies.txt -X GET "http://localhost:8000/posts/2"
```

```shell
# Удаление поста
curl -b cookies.txt -X DELETE "http://localhost:8000/posts/1"

curl -b cookies.txt -X GET "http://localhost:8000/posts/1"
```