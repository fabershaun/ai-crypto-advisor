from enum import Enum

from pydantic import BaseModel


class VoteContentType(str, Enum):
    NEWS = "NEWS"
    SOCIAL = "SOCIAL"
    AI_INSIGHT = "AI_INSIGHT"
    MEME = "MEME"


class VoteValue(str, Enum):
    UP = "UP"
    DOWN = "DOWN"


class VoteIn(BaseModel):
    content_type: VoteContentType
    content_id: str
    vote: VoteValue


class VoteOut(BaseModel):
    content_type: VoteContentType
    content_id: str
    vote: VoteValue
