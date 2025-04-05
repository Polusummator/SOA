import datetime
import bcrypt

from sqlalchemy import create_engine, Column, Integer, String, Date, DateTime, ForeignKey
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker, declarative_base

import schemas

DATABASE_URL = "postgresql://user:password@user-service-db:5432/db"
Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)

class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    bio = Column(String)
    birthday = Column(Date)
    phone_number = Column(String)
    second_email = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)

class UsersDB:
    def __init__(self):
        self.engine = create_engine(DATABASE_URL)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def create_user(self, user: schemas.UserAuth):
        hashed_password = bcrypt.hashpw(user.password.encode(), bcrypt.gensalt()).decode()
        time_now = datetime.datetime.now()
        try:
            with self.Session() as session:
                new_user = User(
                    username=user.username,
                    password=hashed_password,
                    email=user.email,
                )
                session.add(new_user)
                session.flush()
                new_profile = Profile(
                    user_id=new_user.id,
                    created_at=time_now,
                    updated_at=time_now,
                )
                session.add(new_profile)
                session.commit()
        except SQLAlchemyError:
            raise ValueError("Username/email already exists")

    def update_profile(self, profile: schemas.Profile):
        time_now = datetime.datetime.now()
        with self.Session() as session:
            db_profile = session.query(Profile).filter(Profile.user_id == profile.user_id).first()
            if db_profile:
                for key, value in profile.model_dump(exclude_unset=True).items():
                    setattr(db_profile, key, value)
                db_profile.updated_at = time_now
                session.commit()
            else:
                raise ValueError("Profile with id {} not found".format(profile.user_id))

    def get_user_by_username(self, username):
        with self.Session() as session:
            return session.query(User).filter(User.username == username).first()

    def get_profile_by_userid(self, userid):
        with self.Session() as session:
            return session.query(Profile).filter(Profile.user_id == userid).first()

    def delete_user(self, user_id: int):
        with self.Session() as session:
            user = session.query(User).filter(User.id == user_id).first()
            if user:
                session.delete(user)
                session.commit()

    def get_all_users(self):
        with self.Session() as session:
            return session.query(User).all()

    def delete_all_users(self):
        with self.Session() as session:
            session.query(Profile).delete()
            session.query(User).delete()
            session.commit()
