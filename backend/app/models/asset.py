from sqlalchemy import Column, ForeignKey, Integer, String, UniqueConstraint

from app.core.database import Base


class UserAsset(Base):
    __tablename__ = "user_assets"
    __table_args__ = (
        UniqueConstraint("user_id", "asset_symbol", name="uq_user_asset"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    asset_symbol = Column(String, nullable=False)
