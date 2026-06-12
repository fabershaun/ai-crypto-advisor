from enum import Enum

from pydantic import BaseModel


class InvestorType(str, Enum):
    HODLER = "HODLER"
    DAY_TRADER = "DAY_TRADER"
    SWING_TRADER = "SWING_TRADER"
    BEGINNER = "BEGINNER"


class ContentType(str, Enum):
    NEWS = "NEWS"
    CHARTS = "CHARTS"
    SOCIAL = "SOCIAL"
    FUN = "FUN"


class PreferencesIn(BaseModel):
    investor_type: InvestorType
    content_types: list[ContentType]
    assets: list[str]


class PreferencesOut(BaseModel):
    investor_type: InvestorType | None = None
    content_types: list[ContentType] = []
    assets: list[str] = []
