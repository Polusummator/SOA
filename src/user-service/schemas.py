from pydantic import BaseModel, EmailStr, Field
from pydantic_extra_types.phone_numbers import PhoneNumber
from datetime import date
from typing import Optional

PhoneNumber.phone_format = 'E164'

class UserAuth(BaseModel):
    username: str = Field(..., max_length=50)
    password: str = Field(..., max_length=50)
    email: EmailStr


class ProfileUpdate(BaseModel):
    first_name: Optional[str] = Field(None, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)
    bio: Optional[str] = Field(None, max_length=250)
    birthday: Optional[date] = None
    phone_number: Optional[PhoneNumber] = None
    second_email: Optional[EmailStr] = None

    class Config:
        from_attributes = True


class Profile(ProfileUpdate):
    user_id: int

