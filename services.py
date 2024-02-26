import database as _database
import models as _models
import schemas as _schemas

import fastapi as _fastapi
import fastapi.security as _security
import sqlalchemy.orm as _orm
import passlib.hash as _hash
import jwt as _jwt
import datetime as _dt

oauth2_scheme = _security.OAuth2PasswordBearer(tokenUrl="api/token")
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
                               hashed_password=_hash.bcrypt.hash(member.password))
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
    member_obj = _schemas.MemberBase.from_orm(member)
    token = _jwt.encode(member_obj.dict(), SECRET_KEY)
    return dict(access_token=token, token_type="bearer")

async def get_current_member(db: _orm.Session = _fastapi.Depends(get_db), 
                             token: str = _fastapi.Depends(oauth2_scheme)):
    try:
        payload = _jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        member = db.query(_models.Member).filter(_models.Member.email == payload.get("email")).first()
    except:
        raise _fastapi.HTTPException(status_code=401, detail="Invalid email or password")
    
    return _schemas.Member.from_orm(member)

async def create_item(member: _schemas.Member , 
                      item: _schemas.ItemCreate, 
                      db: _orm.Session ):
    if member.employee_role == "admin":
        raise _fastapi.HTTPException(status_code=400, detail="Admins cannot create items")
    db_item = _models.Item(**item.dict(), owner_id=member.id)
    db.add(db_item)
    db.commit()
    await create_log(member, _schemas.LogCreate(log="create item", object_id=db_item.id), db)
    db.refresh(db_item)
    return _schemas.Item.from_orm(db_item)

# it returns all items for the superadmin and admin, and only the user's items for the basic user
async def get_items(skip: int, limit: int, member: _schemas.Member, db: _orm.Session):
    if member.employee_role == "superadmin" or member.employee_role == "admin":
        items = db.query(_models.Item).offset(skip).limit(limit).all()
    else:
        items = db.query(_models.Item).filter(_models.Item.owner_id == member.id).offset(skip).limit(limit).all()
    
    return list(map(_schemas.Item.from_orm, items))

async def _item_selector(item_id: int, member: _schemas.Member, db: _orm.Session):
    if member.employee_role == "superadmin" or member.employee_role == "admin":
        item =  db.query(_models.Item).filter(_models.Item.id == item_id).first()
    else:
        item =  ( 
            db.query(_models.Item)
                .filter_by(owner_id=member.id)
                .filter(_models.Item.id == item_id).first()
        )
    if not item:
        raise _fastapi.HTTPException(status_code=404, detail="Item not found")
    
    return item

async def get_item(item_id: int, member: _schemas.Member, db: _orm.Session):
    return _schemas.Item.from_orm(await _item_selector(item_id, member, db))

async def delete_item(item_id: int, member: _schemas.Member, db: _orm.Session):
    item = await _item_selector(item_id, member, db)
    db.delete(item)
    db.commit()
    await create_log(member, _schemas.LogCreate(log="delete item", object_id=item.id), db)

async def update_item(item_id: int, item: _schemas.ItemCreate, member: _schemas.Member, db: _orm.Session):
    if member.employee_role == "user":
        raise _fastapi.HTTPException(status_code=400, detail="Users cannot update items")
    db_item = await _item_selector(item_id, member, db)

    for key, value in item.dict().items():
        setattr(db_item, key, value)
    setattr(db_item, "date_last_updated", _dt.datetime.now().isoformat())

    db.commit()
    db.refresh(db_item)
    await create_log(member, _schemas.LogCreate(log="update item", object_id=db_item.id), db)
    return _schemas.Item.from_orm(db_item)



# netleşdir
async def get_members(skip: int, limit: int, member: _schemas.Member, db: _orm.Session):
    if member.employee_role == "user":
        raise _fastapi.HTTPException(status_code=400, detail="Users cannot view others")
    if member.employee_role == "admin":
        members = db.query(_models.Member).filter(_models.Member.employee_role == "user").offset(skip).limit(limit).all()
    else:
        members = db.query(_models.Member).filter(_models.Member.employee_role != "superadmin").offset(skip).limit(limit).all()
    return list(map(_schemas.Member.from_orm, members))

async def create_member(current_member: _schemas.Member, member: _schemas.MemberCreate, db: _orm.Session):
    if current_member.employee_role == "user" or current_member.employee_role == "admin":
        raise _fastapi.HTTPException(status_code=400, detail="Only superadmins can create members")
    
    db_member = await get_user_by_email(member.email, db)
    if db_member:
        raise _fastapi.HTTPException(status_code=400, detail="Email already registered")

    db_member = await get_user_by_role("superadmin", db)
    if db_member and member.employee_role == "superadmin":
        raise _fastapi.HTTPException(status_code=400, detail="There can be at most one superadmin in the organization!")
    
    new_member = _models.Member(email=member.email, name=member.name, 
                               surname=member.surname, employee_role=member.employee_role, 
                               hashed_password=_hash.bcrypt.hash(member.password),
                                date_created = _dt.datetime.now().isoformat(),
                                date_last_updated = _dt.datetime.now().isoformat())


    db.add(new_member)
    db.commit()
    db.refresh(new_member)
    await create_log(current_member, _schemas.LogCreate(log="create member", object_id=new_member.id), db)
    return _schemas.Member.from_orm(new_member)

async def get_member(member_id: int, member: _schemas.Member, db: _orm.Session):
    existingmember = db.query(_models.Member).filter(_models.Member.id == member_id).first()
    if not existingmember:
        raise _fastapi.HTTPException(status_code=404, detail="Member not found")
    
    if member.employee_role == "admin":
            if existingmember.employee_role == "superadmin" or ( existingmember.employee_role == "admin" and  not existingmember.id == member.id):
                raise _fastapi.HTTPException(status_code=400, detail="Admins cannot view superadmins and other admins")
            
    elif member.employee_role == "user":
        if not existingmember.id == member.id:
            raise _fastapi.HTTPException(status_code=400, detail="Basic users can only read themselves")
        
    return _schemas.Member.from_orm(existingmember)

async def delete_member(member_id: int, member: _schemas.Member, db: _orm.Session):
    if member.employee_role == "user" or member.employee_role == "admin":
        raise _fastapi.HTTPException(status_code=400, detail="Only superadmins can delete members")
    existingmember = db.query(_models.Member).filter(_models.Member.id == member_id).first()
    if not existingmember:
        raise _fastapi.HTTPException(status_code=404, detail="Member not found")
    if existingmember.employee_role == "superadmin":
        raise _fastapi.HTTPException(status_code=400, detail="Superadmin cannot be deleted")
    
    db.delete(existingmember)
    db.commit()
    await create_log(member, _schemas.LogCreate(log="delete member", object_id=existingmember.id), db)

async def update_member(member_id: int, member: _schemas.MemberUpdate, current_member: _schemas.Member, db: _orm.Session):
    db_member = db.query(_models.Member).filter(_models.Member.id == member_id).first()
    if not db_member:
        raise _fastapi.HTTPException(status_code=404, detail="Member not found")
    
    if current_member.employee_role == "admin":
        if db_member.employee_role == "superadmin" or ( db_member.employee_role == "admin" and  not db_member.id == current_member.id):
            raise _fastapi.HTTPException(status_code=400, detail="Admins cannot update superadmins and other admins")
    elif current_member.employee_role == "user":
        if not db_member.id == current_member.id:
            raise _fastapi.HTTPException(status_code=400, detail="Basic users can only update themselves")

    if not db_member.active == member.active:
        if current_member.employee_role == "superadmin" and db_member.employee_role == "superadmin":
            raise _fastapi.HTTPException(status_code=400, detail="Superadmins cannot suspend himself/herself")
        if current_member.employee_role == "admin" and db_member.id == current_member.id:
            raise _fastapi.HTTPException(status_code=400, detail="Admins cannot suspend themselves")
        if current_member.employee_role == "user":
            raise _fastapi.HTTPException(status_code=400, detail="Basic users cannot (un)suspend anyone")
        
        if member.active == False:
            db_member.suspended_by_id = current_member.id
        else:
            if ( not db_member.suspended_by_id == current_member.id ) and (not current_member.employee_role == "superadmin"):
                raise _fastapi.HTTPException(status_code=400, detail="Only the admin who suspended the member can unsuspend him/her")
            elif db_member.suspended_by_id == current_member.id or current_member.employee_role == "superadmin":
                db_member.suspended_by_id = None

    db_member.date_last_updated = _dt.datetime.now().isoformat()
    db_member.last_updated_by_id = current_member.id
    for key, value in member.dict().items():
        setattr(db_member, key, value)

    db.commit()
    db.refresh(db_member)
    await create_log(current_member, _schemas.LogCreate(log="update member", object_id=db_member.id), db)
    return _schemas.Member.from_orm(db_member)

async def get_logs(skip: int, limit: int, member: _schemas.Member, db: _orm.Session):
    if member.employee_role == "user":
        raise _fastapi.HTTPException(status_code=400, detail="Users cannot view logs")
    logs = db.query(_models.Logs).offset(skip).limit(limit).all()
    return list(map(_schemas.LogCreate.from_orm, logs))

async def create_log(member: _schemas.Member, log: _schemas.LogCreate, db: _orm.Session):
    db_log = _models.Logs(**log.dict(), subject_id=member.id, subject_email=member.email)
    db.add(db_log)
    db.commit()
    db.refresh(db_log)

async def create_organization(member: _schemas.Member, organization:_schemas.OrganizationCreate, db: _orm.Session):
    if db.query(_models.Organization).first():
        raise _fastapi.HTTPException(status_code=400, detail="Organization already exists")
    if member.employee_role == "user" or member.employee_role == "admin":
        raise _fastapi.HTTPException(status_code=400, detail="Only superadmins can create the organization")
    org = _models.Organization(name = organization.name)
    db.add(org)
    db.commit()
    db.refresh(org)
    await create_log(member, _schemas.LogCreate(log="create org", object_id = org.id), db)

async def update_organization(organization:_schemas.OrganizationUpdate, db: _orm.Session, member: _schemas.Member):
    if member.employee_role == "user" or member.employee_role == "admin":
        raise _fastapi.HTTPException(status_code=400, detail="Only superadmins can update the organization")
    org = db.query(_models.Organization).first()
    org.is_active = organization.is_active
    db.commit()
    db.refresh(org)
    await create_log(member, _schemas.LogCreate(log="update org", object_id = org.id), db)
    return _schemas.Organization.from_orm(org)