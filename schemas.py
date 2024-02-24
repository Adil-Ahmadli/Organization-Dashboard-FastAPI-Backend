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
    active: bool
    suspended_by_id: int | None
    last_updated_by_id: int | None

    class Config:
        from_attributes=True



class ItemBase(_pydantic.BaseModel):
    name: str
    description: str
    price: float

class ItemCreate(ItemBase):
    class Config:
        from_attributes=True

class Item(ItemBase):
    id: int
    date_created: str
    date_last_updated: str
    owner_id: int

    class Config:
        from_attributes=True