from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.asset import UserAsset
from app.models.preference import UserContentPreference, UserPreference
from app.models.user import User
from app.schemas.preference_schema import PreferencesIn, PreferencesOut

router = APIRouter(prefix="/preferences", tags=["preferences"])


def _get_preferences(db: Session, user_id: int) -> PreferencesOut:
    preference = db.query(UserPreference).filter(UserPreference.user_id == user_id).first()
    content_prefs = (
        db.query(UserContentPreference).filter(UserContentPreference.user_id == user_id).all()
    )
    assets = db.query(UserAsset).filter(UserAsset.user_id == user_id).all()

    return PreferencesOut(
        investor_type=preference.investor_type if preference else None,
        content_types=[c.content_type for c in content_prefs],
        assets=[a.asset_symbol for a in assets],
    )


@router.get("", response_model=PreferencesOut)
def get_preferences(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    return _get_preferences(db, current_user.id)


@router.post("", response_model=PreferencesOut)
def upsert_preferences(
    payload: PreferencesIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    preference = (
        db.query(UserPreference).filter(UserPreference.user_id == current_user.id).first()
    )
    if preference:
        preference.investor_type = payload.investor_type.value
    else:
        db.add(UserPreference(user_id=current_user.id, investor_type=payload.investor_type.value))

    db.query(UserContentPreference).filter(
        UserContentPreference.user_id == current_user.id
    ).delete()
    for content_type in payload.content_types:
        db.add(UserContentPreference(user_id=current_user.id, content_type=content_type.value))

    db.query(UserAsset).filter(UserAsset.user_id == current_user.id).delete()
    for asset in payload.assets:
        db.add(UserAsset(user_id=current_user.id, asset_symbol=asset))

    db.commit()

    return _get_preferences(db, current_user.id)
