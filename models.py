from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from passlib import hash
import datetime as _dt

from database import Base

class Member(Base):
    __tablename__ = "members"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    surname = Column(String, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    employee_role = Column(String, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    date_created = Column(String, default=_dt.datetime.now().isoformat(), nullable=False)
    date_last_updated = Column(String, default=_dt.datetime.now().isoformat(), nullable=False)
    active = Column(Boolean, default=True, nullable=False)
    suspended_by_id = Column(Integer, ForeignKey('members.id', ondelete='SET NULL'), default=None, nullable=True)
    last_updated_by_id = Column(Integer, ForeignKey('members.id', ondelete='SET NULL'), default=None, nullable=True)

    suspended_by = relationship("Member", foreign_keys=[suspended_by_id])
    last_updated_by = relationship("Member", foreign_keys=[last_updated_by_id])
    children = relationship("Item", cascade="all, delete")
    logs = relationship("Logs", cascade="all, delete")


    def verify_password(self, password: str):
        return hash.bcrypt.verify(password, self.hashed_password)
    
    def __repr__(self):
        return f"<Member: {self.name} {self.surname} {self.email} {self.employee_role}>"

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(String, index=True, nullable=False)
    price = Column(Float, index=True, nullable=False)
    date_created = Column(String, default=_dt.datetime.now().isoformat(), nullable=False)
    date_last_updated = Column(String, default=_dt.datetime.now().isoformat(), nullable=False)
    owner_id = Column(Integer, ForeignKey('members.id', ondelete='CASCADE'), nullable=False)
    members = relationship("Member", foreign_keys=[owner_id])

    def __repr__(self):
        return f"<Item: {self.name}, {self.price} >"

class Logs(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(Integer, ForeignKey('members.id', ondelete='CASCADE'), nullable=False)
    subject_email = Column(String, nullable=False)
    object_id = Column(Integer, nullable=False)
    log = Column(String, nullable=False)
    date_created = Column(String, default=_dt.datetime.now().isoformat(), nullable=False)
    members = relationship("Member", foreign_keys=[subject_id])

    def __repr__(self):
        return f"<Log: {self.log} >"
    
class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    def __repr__(self):
        return f"<Organization: {self.name} >"