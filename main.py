import fastapi as _fastapi
import fastapi.security as _security
import sqlalchemy.orm as _orm

import services as _services, models as _models, database as _database, schemas as _schemas

app = _fastapi.FastAPI()


@app.post("/register")
async def register(member: _schemas.MemberCreate, db: _orm.Session = _fastapi.Depends(_services.get_db)):
    db_member = await _services.get_user_by_email(member.email, db)
    if db_member:
        raise _fastapi.HTTPException(status_code=400, detail="Email already registered")

    db_member = await _services.get_user_by_role(member.employee_role, db)
    if db_member:
        raise _fastapi.HTTPException(status_code=400, detail="There can be at most one superadmin in the organization!")

    member = await _services.register_member(member, db)
    return await _services.create_token(member)

@app.post("/api/token")
async def generate_token(form_data: _security.OAuth2PasswordRequestForm = _fastapi.Depends(),
                          db: _orm.Session = _fastapi.Depends(_services.get_db)):
    user = await _services.authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise _fastapi.HTTPException(status_code=401, detail="Invalid email or password")
    
    return await _services.create_token(user)

@app.get("/items")
async def read_items(skip: int = 0, limit: int = 10, db: _orm.Session = _fastapi.Depends(_services.get_db)):
    items = db.query(_models.Item).offset(skip).limit(limit).all()
    return items

@app.get("/members")
async def read_members(skip: int = 0, limit: int = 10, db: _orm.Session = _fastapi.Depends(_services.get_db)):
    members = db.query(_models.Member).offset(skip).limit(limit).all()
    return members
