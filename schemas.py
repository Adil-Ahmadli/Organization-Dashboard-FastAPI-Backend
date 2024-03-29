import datetime as _dt
import pydantic as _pydantic



class MemberBase(_pydantic.BaseModel):
    email: str
    name: str
    surname: str
    employee_role: str
    class Config:
        from_attributes=True

class MemberCreate(MemberBase):
    password: str

    class Config:
        from_attributes=True
        
class MemberLogin(_pydantic.BaseModel):
    email: str
    password: str

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


class MemberUpdate(_pydantic.BaseModel):
    name: str
    surname: str
    active: bool

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


class LogCreate(_pydantic.BaseModel):
    object_id: int
    log: str

    class Config:
        from_attributes=True

class Log(LogCreate):
    id: int
    date_created: str
    subject_id: int
    subject_email: str
    class Config:
        from_attributes=True

class Organization(_pydantic.BaseModel):
    id: int
    name: str
    is_active: bool
    
    class Config:
        from_attributes=True

class OrganizationUpdate(_pydantic.BaseModel):
    is_active: bool
    
    class Config:
        from_attributes=True

class OrganizationCreate(_pydantic.BaseModel):
    name: str
    
    class Config:
        from_attributes=True
