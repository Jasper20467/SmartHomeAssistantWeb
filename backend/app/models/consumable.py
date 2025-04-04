from sqlalchemy import Column, Integer, String, Text, Date, DateTime, func
from app.database.database import Base

class Consumable(Base):
    __tablename__ = "consumables"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False)
    installation_date = Column(Date, nullable=False)
    lifetime_days = Column(Integer, nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
