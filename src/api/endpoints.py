from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database.database import get_async_session 
from api.servise import ItemService
from api.shema import Create_task, ResponseTask  


router = APIRouter(prefix="/api/v1/task", tags=["task"])



@router.post("/", response_model=ResponseTask) 
async def create_task(task: Create_task, session: AsyncSession = Depends(get_async_session)):
    try:
        service = ItemService()
        created_task = await service.create_item(task, session)
        return created_task
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=500, detail=f"Ошибка базы данных: {e}")








