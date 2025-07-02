
from sqlalchemy.orm import relationship
from app.database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, JSON, Text

class Dashboard(Base):
    __tablename__ = "dashboards"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    data = Column(JSON, nullable=False) # You can store the entire JSON as string
    thumbnail = Column(Text)

    # Optional: Relationship back to user
    user = relationship("User", back_populates="dashboards")
