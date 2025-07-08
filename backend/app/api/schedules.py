from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
from datetime import datetime, date
from pydantic import BaseModel, Field
from app.database.database import get_db
from app.models.schedule import Schedule

router = APIRouter()

# Pydantic models for request/response
class ScheduleBase(BaseModel):
    title: str
    description: Optional[str] = None  # Allow None for optional fields
    start_time: datetime
    end_time: Optional[datetime] = None

class ScheduleCreate(ScheduleBase):
    pass

class ScheduleUpdate(ScheduleBase):
    title: str = None
    start_time: datetime = None

class ScheduleResponse(ScheduleBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

@router.get("/", response_model=List[ScheduleResponse])
async def get_schedules(
    skip: int = 0, 
    limit: int = 100,
    date_filter: Optional[str] = Query(None, description="Filter by date (YYYY-MM-DD format)"),
    db: AsyncSession = Depends(get_db)
):
    """Get all schedules with pagination and optional date filtering"""
    query = select(Schedule)
    
    # Add date filtering if provided
    if date_filter:
        try:
            filter_date = datetime.strptime(date_filter, "%Y-%m-%d").date()
            # Filter schedules that start on the specified date
            query = query.filter(
                Schedule.start_time >= datetime.combine(filter_date, datetime.min.time()),
                Schedule.start_time < datetime.combine(filter_date, datetime.max.time())
            )
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    result = await db.execute(query.offset(skip).limit(limit))
    schedules = result.scalars().all()
    return schedules

@router.post("/", response_model=ScheduleResponse, status_code=status.HTTP_201_CREATED)
async def create_schedule(
    schedule: ScheduleCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new schedule"""
    db_schedule = Schedule(
        title=schedule.title,
        description=schedule.description,
        start_time=schedule.start_time,
        end_time=schedule.end_time
    )
    db.add(db_schedule)
    await db.commit()
    await db.refresh(db_schedule)
    return db_schedule

@router.get("/{schedule_id}", response_model=ScheduleResponse)
async def get_schedule(
    schedule_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific schedule by ID"""
    result = await db.execute(select(Schedule).filter(Schedule.id == schedule_id))
    schedule = result.scalars().first()
    
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    return schedule

@router.put("/{schedule_id}", response_model=ScheduleResponse)
async def update_schedule(
    schedule_id: int,
    schedule: ScheduleUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a schedule"""
    result = await db.execute(select(Schedule).filter(Schedule.id == schedule_id))
    db_schedule = result.scalars().first()
    
    if not db_schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    update_data = schedule.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_schedule, key, value)
    
    await db.commit()
    await db.refresh(db_schedule)
    return db_schedule

@router.delete("/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_schedule(
    schedule_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a schedule"""
    result = await db.execute(select(Schedule).filter(Schedule.id == schedule_id))
    db_schedule = result.scalars().first()
    
    if not db_schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    await db.delete(db_schedule)
    await db.commit()
    return None

@router.get("/by-date/{date_str}", response_model=List[ScheduleResponse])
async def get_schedules_by_date(
    date_str: str,
    db: AsyncSession = Depends(get_db)
):
    """Get schedules for a specific date (YYYY-MM-DD format)"""
    try:
        filter_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    result = await db.execute(
        select(Schedule).filter(
            Schedule.start_time >= datetime.combine(filter_date, datetime.min.time()),
            Schedule.start_time < datetime.combine(filter_date, datetime.max.time())
        )
    )
    schedules = result.scalars().all()
    return schedules
