from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.models.vote import Vote
from app.schemas.vote_schema import VoteIn, VoteOut

router = APIRouter(prefix="/votes", tags=["votes"])


@router.post("", response_model=VoteOut)
def upsert_vote(
    payload: VoteIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    vote = (
        db.query(Vote)
        .filter(
            Vote.user_id == current_user.id,
            Vote.content_type == payload.content_type.value,
            Vote.content_id == payload.content_id,
        )
        .first()
    )
    if vote:
        vote.vote = payload.vote.value
    else:
        vote = Vote(
            user_id=current_user.id,
            content_type=payload.content_type.value,
            content_id=payload.content_id,
            vote=payload.vote.value,
        )
        db.add(vote)

    db.commit()
    db.refresh(vote)

    return VoteOut(content_type=vote.content_type, content_id=vote.content_id, vote=vote.vote)
