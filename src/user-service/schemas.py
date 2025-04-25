from pydantic import BaseModel, EmailStr, Field, PastDate
from pydantic_extra_types.phone_numbers import PhoneNumber
from typing import Optional
import datetime

PhoneNumber.phone_format = 'E164'

class UserAuth(BaseModel):
    username: str = Field(..., max_length=50)
    password: str = Field(..., max_length=50)
    email: EmailStr

class UserOut(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime.datetime

class ProfileUpdate(BaseModel):
    first_name: Optional[str] = Field(None, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)
    bio: Optional[str] = Field(None, max_length=250)
    birthday: Optional[PastDate] = None
    phone_number: Optional[PhoneNumber] = None
    second_email: Optional[EmailStr] = None

    class Config:
        from_attributes = True


class Profile(ProfileUpdate):
    user_id: int

