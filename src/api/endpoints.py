from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database.database import get_async_session
from api.servise import ItemService
from api.shema import Create_task, ResponseTask, Translation_completed_task


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


@router.delete("/{task_id: int}")
async def delete_task(task_id: int, session: AsyncSession = Depends(get_async_session)):
    try:
        service = ItemService()
        delete_task = await service.delete_item(task_id, session)
        return delete_task
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=500, detail=f"Ошибка базы данных: {e}")


@router.patch("/{task_id;int},response_model= Translation_completed_task")
async def translation_into_completed(task: Translation_completed_task, task_id: int, session: AsyncSession = Depends(get_async_session)):
    try:
        service = ItemService()
        translation_into_completed_task = await service.translation_into_completed(task, task_id, session)
        return translation_into_completed_task
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=500, detail=f"Ошибка базы данных: {e}")
