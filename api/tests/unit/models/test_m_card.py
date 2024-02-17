import pytest
from fastapi import status
from httpx import AsyncClient
from httpx_auth import Basic
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from models import User, Card
from crud.user import create as create_user
from schemas.user import UserCreate

@pytest.mark.asyncio()
class TestCardModel:

    async def test_create_card(self, async_db: AsyncSession, create_user: User) -> None:

        card = Card(owner=create_user)
        async_db.add(card)

        await async_db.commit()
        await async_db.refresh(card)

        db_card = await async_db.scalar(
            select(Card)
                .where(Card.id == card.id)
                .options(joinedload(Card.owner))
                .limit(1)
        )

        assert db_card.id == card.id
        assert create_user == card.owner
