from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class UserConnection(Base):
    __tablename__ = "user_connections"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    db_type = Column(String)         # e.g., "PostgreSQL", "MySQL"
    host = Column(String)
    port = Column(Integer)
    database = Column(String)
    username = Column(String)
    encrypted_password = Column(String)        # Consider encrypting this
    sslmode = Column(String)

    # Optional: Add relationship to User
    user = relationship("User", back_populates="connections")


    def get_decrypted_password(self):
        from app.dependencies import decrypt_password
        return decrypt_password(self.encrypted_password)



