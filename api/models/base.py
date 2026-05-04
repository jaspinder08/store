from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, Boolean
from api.core.database import Base

class TimestampModel(Base):
    __abstract__ = True
    
    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
