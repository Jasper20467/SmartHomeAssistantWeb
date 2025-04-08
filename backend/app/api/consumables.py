from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
from datetime import date, datetime
from pydantic import BaseModel
from app.database.database import get_db
from app.models.consumable import Consumable

router = APIRouter()

# Pydantic models
class ConsumableBase(BaseModel):
    name: str
    category: str
    installation_date: date
    lifetime_days: int
    notes: Optional[str] = None  # 修改為可選


class ConsumableCreate(ConsumableBase):
    pass


class ConsumableUpdate(BaseModel):
    name: str = None
    category: str = None
    installation_date: date = None
    lifetime_days: int = None
    notes: str = None


class ConsumableResponse(ConsumableBase):
    id: int
    created_at: datetime
    updated_at: datetime
    days_remaining: int = None

    class Config:
        orm_mode = True


def calculate_days_remaining(installation_date: date, lifetime_days: int) -> int:
    """Calculate the remaining days for a consumable."""
    days_passed = (date.today() - installation_date).days
    return max(0, lifetime_days - days_passed)


@router.get("/", response_model=List[ConsumableResponse])
async def get_consumables(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """Get all consumables with pagination."""
    result = await db.execute(select(Consumable).offset(skip).limit(limit))
    consumables = result.scalars().all()

    return [
        {
            "id": item.id,
            "name": item.name,
            "category": item.category,
            "installation_date": item.installation_date,
            "lifetime_days": item.lifetime_days,
            "notes": item.notes,
            "created_at": item.created_at,
            "updated_at": item.updated_at,
            "days_remaining": calculate_days_remaining(item.installation_date, item.lifetime_days),
        }
        for item in consumables
    ]


@router.post("/", response_model=ConsumableResponse, status_code=status.HTTP_201_CREATED)
async def create_consumable(consumable: ConsumableCreate, db: AsyncSession = Depends(get_db)):
    """Create a new consumable item."""
    db_consumable = Consumable(**consumable.dict())
    db.add(db_consumable)
    await db.commit()
    await db.refresh(db_consumable)

    return {
        "id": db_consumable.id,
        "name": db_consumable.name,
        "category": db_consumable.category,
        "installation_date": db_consumable.installation_date,
        "lifetime_days": db_consumable.lifetime_days,
        "notes": db_consumable.notes,
        "created_at": db_consumable.created_at,
        "updated_at": db_consumable.updated_at,
        "days_remaining": calculate_days_remaining(db_consumable.installation_date, db_consumable.lifetime_days),
    }


@router.get("/{consumable_id}", response_model=ConsumableResponse)
async def get_consumable(consumable_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific consumable by ID."""
    result = await db.execute(select(Consumable).filter(Consumable.id == consumable_id))
    consumable = result.scalars().first()

    if not consumable:
        raise HTTPException(status_code=404, detail="Consumable not found")

    return {
        "id": consumable.id,
        "name": consumable.name,
        "category": consumable.category,
        "installation_date": consumable.installation_date,
        "lifetime_days": consumable.lifetime_days,
        "notes": consumable.notes,
        "created_at": consumable.created_at,
        "updated_at": consumable.updated_at,
        "days_remaining": calculate_days_remaining(consumable.installation_date, consumable.lifetime_days),
    }


@router.put("/{consumable_id}", response_model=ConsumableResponse)
async def update_consumable(consumable_id: int, consumable: ConsumableUpdate, db: AsyncSession = Depends(get_db)):
    """Update a consumable."""
    result = await db.execute(select(Consumable).filter(Consumable.id == consumable_id))
    db_consumable = result.scalars().first()

    if not db_consumable:
        raise HTTPException(status_code=404, detail="Consumable not found")

    update_data = consumable.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_consumable, key, value)

    await db.commit()
    await db.refresh(db_consumable)

    return {
        "id": db_consumable.id,
        "name": db_consumable.name,
        "category": db_consumable.category,
        "installation_date": db_consumable.installation_date,
        "lifetime_days": db_consumable.lifetime_days,
        "notes": db_consumable.notes,
        "created_at": db_consumable.created_at,
        "updated_at": db_consumable.updated_at,
        "days_remaining": calculate_days_remaining(db_consumable.installation_date, db_consumable.lifetime_days),
    }


@router.delete("/{consumable_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_consumable(consumable_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a consumable by ID."""
    result = await db.execute(select(Consumable).filter(Consumable.id == consumable_id))
    db_consumable = result.scalars().first()

    if not db_consumable:
        raise HTTPException(status_code=404, detail="Consumable not found")

    await db.delete(db_consumable)
    await db.commit()
