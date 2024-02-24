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

    parent = relationship("Member", remote_side=[id], backref="children", foreign_keys=[suspended_by_id, last_updated_by_id])
    children = relationship("Item", back_populates="parent", cascade="all, delete")

    def verify_password(self, password: str):
        return hash.bcrypt.verify(password, self.hashed_password)
    
    def __repr__(self):
        return f"<Member {self.name} {self.surname} {self.email} {self.employee_role}>"

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(String, index=True, nullable=False)
    price = Column(Float, index=True, nullable=False)
    date_created = Column(String, default=_dt.datetime.now().isoformat(), nullable=False)
    date_last_updated = Column(String, default=_dt.datetime.now().isoformat(), nullable=False)
    owner_id = Column(Integer, ForeignKey('members.id', ondelete='CASCADE'), nullable=False)
    members = relationship("Member", backref="other_entries")
