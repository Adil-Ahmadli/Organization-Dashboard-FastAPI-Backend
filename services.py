import database as _database
import models as _models
import schemas as _schemas

import sqlalchemy.orm as _orm
import passlib.hash as _hash
import jwt as _jwt

SECRET_KEY = "HAH73-JABsd42Kfim1#%$C"

def create_database():
    return _database.Base.metadata.create_all(bind=_database.engine)

def get_db():
    db = _database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_user_by_email(email: str, db: _orm.Session):
    return db.query(_models.Member).filter(_models.Member.email == email).first()

async def get_user_by_role(role: str, db: _orm.Session):
    return db.query(_models.Member).filter(_models.Member.employee_role == role).first()

async def register_member(member: _schemas.MemberCreate, db: _orm.Session):
    db_member = _models.Member(email=member.email, name=member.name, 
                               surname=member.surname, employee_role=member.employee_role, 
                               hashed_password=_hash.bcrypt.hash(member.hashed_password))
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    return db_member

async def authenticate_user(email: str, password: str, db: _orm.Session):
    user = await get_user_by_email(email=email, db=db)
    if not user or not user.verify_password(password):
        return False
    return user

async def create_token(member: _models.Member):
    member_obj = _schemas.Member.from_orm(member)
    token = _jwt.encode(member_obj.dict(), SECRET_KEY)
    return dict(access_token=token, token_type="bearer")