from sqlalchemy import Column, Integer, String, ForeignKey, Text, JSON, TIMESTAMP, func
from sqlalchemy.orm import relationship
from app.database import Base

class QueryHistory(Base):
    __tablename__ = "query_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    prompt = Column(Text, nullable=False)
    generated_query = Column(Text)
    status = Column(String(20), nullable=False)
    llm_config = Column(JSON)
    created_at = Column(TIMESTAMP, server_default=func.now())
    generated_query = Column(Text, nullable=True)

    user = relationship("User", back_populates="query_history")
