from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, UniqueConstraint, func

from app.core.database import Base


class Vote(Base):
    __tablename__ = "votes"
    __table_args__ = (
        UniqueConstraint("user_id", "content_type", "content_id", name="uq_user_vote"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content_type = Column(String, nullable=False)
    content_id = Column(String, nullable=False)
    vote = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
