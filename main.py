import fastapi as _fastapi
import fastapi.security as _security
import sqlalchemy.orm as _orm
from fastapi.middleware.cors import CORSMiddleware

import services as _services, models as _models, database as _database, schemas as _schemas

app = _fastapi.FastAPI()
app.add_middleware(CORSMiddleware, 
                   allow_origins=["*"], 
                   allow_credentials=True, 
                   allow_methods=["*"], 
                   allow_headers=["*"]
                   )
# general routes
@app.post("/register")
async def register(member: _schemas.MemberCreate, db: _orm.Session = _fastapi.Depends(_services.get_db)):
    db_member = await _services.get_user_by_email(member.email, db)
    if db_member:
        raise _fastapi.HTTPException(status_code=400, detail="Email already registered")

    db_member = await _services.get_user_by_role("superadmin", db)
    if db_member and member.employee_role == "superadmin":
        raise _fastapi.HTTPException(status_code=400, detail="There can be at most one superadmin in the organization!")

    member = await _services.register_member(member, db)
    return await _services.create_token(member)

@app.post("/api/login")
async def login(member: _schemas.MemberLogin,
		 db: _orm.Session = _fastapi.Depends(_services.get_db)):
    user = await _services.authenticate_user(member.email, member.password, db)
    if not user:
        raise _fastapi.HTTPException(status_code=401, detail="Invalid email or password")
    
    return await _services.create_token(user)

@app.post("/api/token")
async def generate_token(form_data: _security.OAuth2PasswordRequestForm = _fastapi.Depends(),
                          db: _orm.Session = _fastapi.Depends(_services.get_db)):
    user = await _services.authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise _fastapi.HTTPException(status_code=401, detail="Invalid email or password")
    
    return await _services.create_token(user)


# member routes
@app.get("/api/members/me", response_model=_schemas.Member)
async def get_me(current_member: _schemas.Member = _fastapi.Depends(_services.get_current_member)):
    return current_member

@app.get("/api/members", response_model=list[_schemas.Member])
async def read_members(skip: int = 0, limit: int = 100,
                       current_member: _schemas.Member = _fastapi.Depends(_services.get_current_member),
                       db: _orm.Session = _fastapi.Depends(_services.get_db)):
    return await _services.get_members(skip, limit, current_member, db)
 
@app.post("/api/members")
async def create_member(member: _schemas.MemberCreate, 
                        db: _orm.Session = _fastapi.Depends(_services.get_db),
                        current_member: _schemas.Member = _fastapi.Depends(_services.get_current_member)):
    return await _services.create_member(current_member, member, db)

@app.get("/api/members/{member_id}", status_code=200)
async def read_member(member_id: int,
                    db: _orm.Session = _fastapi.Depends(_services.get_db),
                    current_member: _schemas.Member = _fastapi.Depends(_services.get_current_member)):
            return await _services.get_member(member_id, current_member, db)

@app.delete("/api/members/{member_id}", status_code=204)
async def delete_member(member_id: int,
                        db: _orm.Session = _fastapi.Depends(_services.get_db),
                        current_member: _schemas.Member = _fastapi.Depends(_services.get_current_member)):
        await _services.delete_member(member_id, current_member, db)
        return {'detail': 'Member deleted successfully'}

@app.put("/api/members/{member_id}", status_code=200)
async def update_member(member_id: int,
                        member: _schemas.MemberUpdate,
                        db: _orm.Session = _fastapi.Depends(_services.get_db),
                        current_member: _schemas.Member = _fastapi.Depends(_services.get_current_member)):
        await _services.update_member(member_id, member, current_member, db)
        return {'detail': 'Member updated successfully'}





# item routes
@app.get("/api/items", response_model=list[_schemas.Item])
async def read_items(skip: int = 0, limit: int = 100,
                     member: _schemas.Member = _fastapi.Depends(_services.get_current_member),
                     db: _orm.Session = _fastapi.Depends(_services.get_db)):
        return await _services.get_items(skip, limit, member, db)


@app.post("/api/items")
async def create_item(item: _schemas.ItemCreate, 
                      db: _orm.Session = _fastapi.Depends(_services.get_db),
                      current_member: _schemas.Member = _fastapi.Depends(_services.get_current_member)):
    return await _services.create_item(current_member, item, db)

@app.get("/api/items/{item_id}", status_code=200)
async def read_item(item_id: int, 
                    db: _orm.Session = _fastapi.Depends(_services.get_db),
                    current_member: _schemas.Member = _fastapi.Depends(_services.get_current_member)
                    ):
    return await _services.get_item(item_id, current_member, db)


@app.delete("/api/items/{item_id}", status_code=204)
async def delete_item(item_id: int, 
                    db: _orm.Session = _fastapi.Depends(_services.get_db),
                    current_member: _schemas.Member = _fastapi.Depends(_services.get_current_member)
                    ):
        await _services.delete_item(item_id, current_member, db)
        return {"detail": "Item deleted successfully"}

@app.put("/api/items/{item_id}", status_code=200)
async def update_item(item_id: int,
                        item: _schemas.ItemCreate,
                        db: _orm.Session = _fastapi.Depends(_services.get_db),
                        current_member: _schemas.Member = _fastapi.Depends(_services.get_current_member)
                    ):
        await _services.update_item(item_id, item, current_member, db)
        return {'detail': 'Item updated successfully'}

# log routes
@app.get("/api/logs", response_model=list[_schemas.Log])
async def read_logs(skip: int = 0, limit: int = 100,
                    member: _schemas.Member = _fastapi.Depends(_services.get_current_member),
                    db: _orm.Session = _fastapi.Depends(_services.get_db)):
        return await _services.get_logs(skip, limit, member, db)

# organization routes
@app.post("/api/organizations")
async def create_organization(organization: _schemas.OrganizationCreate,
                              db: _orm.Session = _fastapi.Depends(_services.get_db),
                               member: _schemas.Member = _fastapi.Depends(_services.get_current_member)):
    return await _services.create_organization(member, organization, db)


@app.put("/api/organizations", status_code=200)
async def update_organization(organization: _schemas.OrganizationUpdate,
                              db: _orm.Session = _fastapi.Depends(_services.get_db),
                              member: _schemas.Member = _fastapi.Depends(_services.get_current_member)):
    return await _services.update_organization(organization, db, member)

@app.get("/api/organizations", response_model=list[_schemas.Organization])
async def read_organizations( member: _schemas.Member = _fastapi.Depends(_services.get_current_member),
                             db: _orm.Session = _fastapi.Depends(_services.get_db)):
    return await _services.get_organizations(member, db)