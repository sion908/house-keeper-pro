from datetime import datetime
from typing import AsyncIterator

from fastapi import HTTPException
from sqlalchemy import select, text
from sqlalchemy.dialects.mysql import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.sql.functions import current_timestamp

from models import Card, Place, Stamp, User
from schemas.user import UserCreate


async def get_by_id(db: AsyncSession, card_id: str=None, card: Card=None) -> AsyncIterator[Card]| None:
    if card_id is None and card is not None:
        card_id = card.id
    card = await db.scalar(
        select(Card)
            .where(Card.id == card_id)
            .options(
                joinedload(Card.stamps),
                joinedload(Card.stamps).joinedload(Stamp.place)
            ).limit(1)
    )

    if card and card.stamps:
        # Stamp を Place.id でソートし、Place の id と name のみを抽出
        card.stamps.sort(key=lambda stamp: stamp.place.id)

    return card

async def create_with_stamps(db: AsyncSession, user: User, places: list[Place]) -> Card:
    """create user by email and password"""
    card = Card(owner=user)
    db.add(card)

    await db.commit()
    await db.refresh(card)
    card_id = getattr(card, "id", None)
    if card_id is None:
        raise TimeoutError("dberror")

    stamp_attrs = [{
        "is_stamped": False,
        "card_id": card_id,
        "place_id": p.id
    } for p in places]

    await db.execute(
        Stamp.__table__.insert(),
        stamp_attrs
    )

    await db.commit()
    card = await get_by_id(db=db, card_id=card.id)
    return card
