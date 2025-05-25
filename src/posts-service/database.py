from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base

from contextlib import contextmanager
import datetime

DATABASE_URL = "postgresql://user:password@posts-service-db:5432/db"
Base = declarative_base()

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    is_private = Column(Boolean, default=False)
    creator_id = Column(Integer)


class PostTag(Base):
    __tablename__ = "posts_tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id"))

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, nullable=False)
    created_at = Column(DateTime)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"))
    creator_id = Column(Integer)

class PostsDB:
    def __init__(self):
        self.engine = create_engine(DATABASE_URL)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    @contextmanager
    def get_session(self):
        session = self.Session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def can_access_post(self, post_id, user_id):
        with self.get_session() as session:
            post = session.query(Post).get(post_id)
            if not post:
                return False
            if post.is_private and post.creator_id != user_id:
                return False
            return True

    def create_post(self, title, description, creator_id, is_private, tags):
        with self.get_session() as session:
            post = Post(
                title=title,
                description=description,
                creator_id=creator_id,
                is_private=is_private,
                created_at=datetime.datetime.now(),
                updated_at=datetime.datetime.now()
            )
            session.add(post)
            session.flush()

            for tag_name in tags:
                tag = PostTag(name=tag_name, post_id=post.id)
                session.add(tag)

            return {
                "id": post.id,
                "title": post.title,
                "description": post.description,
                "created_at": post.created_at,
                "updated_at": post.updated_at,
                "is_private": post.is_private,
                "creator_id": post.creator_id,
                "tags": tags
            }

    def delete_post(self, post_id, user_id):
        with self.get_session() as session:
            post = session.query(Post).get(post_id)
            if not post:
                return False

            if post.creator_id != user_id:
                return False

            session.query(PostTag).filter(PostTag.post_id==post_id).delete()

            session.delete(post)
            return True

    def delete_all_posts(self):
        with self.get_session() as session:
            session.query(PostTag).delete()
            session.query(Post).delete()
            session.commit()

    def update_post(self, post_id, title, description, is_private, user_id, tags):
        with self.get_session() as session:
            post = session.query(Post).get(post_id)
            if not post:
                return None

            if post.creator_id != user_id:
                return None

            post.title = title
            post.description = description
            post.is_private = is_private
            post.updated_at = datetime.datetime.now()

            session.query(PostTag).filter(PostTag.post_id==post_id).delete()
            for tag_name in tags:
                tag = PostTag(name=tag_name, post_id=post.id)
                session.add(tag)

            return {
                "id": post.id,
                "title": post.title,
                "description": post.description,
                "created_at": post.created_at,
                "updated_at": post.updated_at,
                "is_private": post.is_private,
                "creator_id": post.creator_id,
                "tags": tags
            }

    def get_post(self, post_id, user_id):
        with self.get_session() as session:
            post = session.query(Post).get(post_id)
            if not post:
                return None

            if post.is_private and post.creator_id != user_id:
                return None

            tags_query = session.query(PostTag).filter(PostTag.post_id==post_id).all()
            tag_names = [tag.name for tag in tags_query]

            return {
                "id": post.id,
                "title": post.title,
                "description": post.description,
                "created_at": post.created_at,
                "updated_at": post.updated_at,
                "is_private": post.is_private,
                "creator_id": post.creator_id,
                "tags": tag_names
            }

    def list_posts(self, page, page_size, user_id):
        with self.get_session() as session:
            query = session.query(Post).filter((Post.is_private == False) | (Post.creator_id == user_id))
            total = query.count()
            posts = query.order_by(Post.created_at.desc()) \
                .offset((page - 1) * page_size) \
                .limit(page_size) \
                .all()

            result = []
            for post in posts:
                tags_query = session.query(PostTag.name).filter(PostTag.post_id == post.id).all()
                tag_names = [tag.name for tag in tags_query]

                result.append({
                    "id": post.id,
                    "title": post.title,
                    "description": post.description,
                    "created_at": post.created_at,
                    "updated_at": post.updated_at,
                    "is_private": post.is_private,
                    "creator_id": post.creator_id,
                    "tags": tag_names
                })

            return {
                "posts": result,
                "total": total,
                "page": page,
                "page_size": page_size
            }

    def create_comment(self, description, post_id, creator_id):
        with self.get_session() as session:
            comment = Comment(
                description=description,
                post_id=post_id,
                creator_id=creator_id,
                created_at=datetime.datetime.now()
            )
            session.add(comment)
            session.flush()

            return {
                "id": comment.id,
                "description": comment.description,
                "created_at": comment.created_at,
                "post_id": comment.post_id,
                "creator_id": comment.creator_id
            }

    def list_comments(self, post_id, user_id, page, page_size):
        with self.get_session() as session:
            post = session.query(Post).get(post_id)
            if not post:
                return None
            if post.is_private and post.creator_id != user_id:
                return None

            query = session.query(Comment).filter(Comment.post_id == post_id)
            total = query.count()
            comments = query.order_by(Comment.created_at.desc()) \
                .offset((page - 1) * page_size) \
                .limit(page_size) \
                .all()

            return {
                "comments": [{
                    "id": c.id,
                    "description": c.description,
                    "created_at": c.created_at,
                    "post_id": c.post_id,
                    "creator_id": c.creator_id
                } for c in comments],
                "total": total,
                "page": page,
                "page_size": page_size
            }