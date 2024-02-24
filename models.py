from sqlalchemy import Column, Integer, String, DateTime
from passlib import hash
import datetime as _dt

from database import Base

class Member(Base):
    __tablename__ = "members"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    surname = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    employee_role = Column(String, index=True)
    hashed_password = Column(String)
    date_created = Column(String, default=_dt.datetime.now().isoformat())
    date_last_updated = Column(String, default=_dt.datetime.now().isoformat())


    def verify_password(self, password: str):
        return hash.bcrypt.verify(password, self.hashed_password)
