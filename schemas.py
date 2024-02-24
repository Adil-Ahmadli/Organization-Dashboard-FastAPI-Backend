import datetime as _dt

import pydantic as _pydantic


class MemberBase(_pydantic.BaseModel):
    email: str
    name: str
    surname: str
    employee_role: str


class MemberCreate(MemberBase):
    hashed_password: str

    class Config:
        from_attributes=True

class Member(MemberBase):
    id: int
    date_created: str
    date_last_updated: str

    class Config:
        from_attributes=True