from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, Text, UniqueConstraint, func

from app.core.database import Base


class AIInsight(Base):
    __tablename__ = "ai_insights"
    __table_args__ = (
        UniqueConstraint("user_id", "generated_date", name="uq_user_ai_insight_date"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    generated_date = Column(Date, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
