User service: `users`, `user_profiles`, `user_roles`

Posts service: `posts`, `posts_likes`, `posts_views`, `comments`, `comments_likes`

Statistics service: `post_stats`, `comments_stats`, `user_stats`

```mermaid

erDiagram

    users ||--o{ user_profiles : "has"
    users ||--o{ user_roles : "has"

    users {
        int id PK
        string username
        string password
        string email
        datetime created_at
    }

    user_profiles {
        int id PK
        int user_id FK
        string full_name
        string bio
        string avatar_url
        string phone_number
        date birthday
    }

    user_roles {
        int id PK
        int user_id FK
        string role
    }



    posts {
        int id PK
        int user_id FK
        string content
        datetime created_at
    }

    posts_likes {
        int id PK
        int post_id FK
        int user_id FK
        datetime liked_at
    }

    posts_views {
        int id PK
        int post_id FK
        int user_id FK
        datetime viewed_at
    }

    comments {
        int id PK
        int post_id FK
        int user_id FK
        int parent_id FK
        string content
        datetime created_at
    }

    comments_likes {
        int id PK
        int comment_id FK
        int user_id FK
        datetime liked_at
    }

    posts ||--o{ posts_likes : "has"
    posts ||--o{ posts_views : "has"
    posts ||--o{ comments : "has"
    comments ||--o{ comments_likes : "has"



    post_stats {
        int id PK
        int post_id FK
        int views
        int likes
        int comments
    }

    user_stats {
        int id PK
        int user_id FK
        int total_posts
        int total_likes
        int total_comments
    }

    comment_stats {
        int id PK
        int comment_id
        int likes
    }



    users ||--o{ posts : "creates"
    users ||--o{ comments : "creates"
    users ||--o{ user_stats : "has"
    posts ||--o{ post_stats : "has"
    comments ||--o{ comment_stats : "has"
```