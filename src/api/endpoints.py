from datetime import date
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from database.database import get_async_session
from api.servise import ItemService
from api.shema import Create_task, ResponseTask, Translation_completed_task, \
    Update_task

router = APIRouter(prefix="/api/v1/task", tags=["Tasks"])


@router.post("/", response_model=ResponseTask)
async def create_task(task: Create_task,
                      session: AsyncSession = Depends(get_async_session)):
    """ Эндпойнт создания списка дел"""
    try:
        service = ItemService()
        created_task = await service.create_item(task, session)
        return created_task
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=500, detail=f"Ошибка базы данных: {e}")


@router.delete("/{task_id: int}")
async def delete_task(task_id: int = Query(description="id задачи"),
                      session: AsyncSession = Depends(get_async_session)):
    """ Эндпойнт удаления списка дел"""
    try:
        service = ItemService()
        delete_task = await service.delete_item(task_id, session)
        return delete_task
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=500, detail=f"Ошибка базы данных: {e}")


@router.patch("/{task_id: int}", response_model=Translation_completed_task)
async def translation_into_completed(task: Translation_completed_task,
                                     task_id: int = Query(
                                         description="id задачи"),
                                     session: AsyncSession = Depends(
                                         get_async_session)):
    """ Эндпойнт перевод в выполненные"""
    try:
        service = ItemService()
        translation_into_completed_task = await service.translation_into_completed(
            task, task_id, session)
        return translation_into_completed_task
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=500, detail=f"Ошибка базы данных: {e}")


@router.patch("/update/{task_id: int}", response_model=Update_task)
async def update_task(task: Update_task,
                      task_id: int = Query(description="id задачи"),

                      session: AsyncSession = Depends(get_async_session)):
    """ Эндпойнт редактирования списка дел"""
    try:
        service = ItemService()
        update_task = await service.update_task(task, task_id, session)
        return update_task
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=500, detail=f"Ошибка базы данных: {e}")


@router.get("/")
async def get_task_list(skip: int = Query(
    0, description="Количество пропускаемых элементов (пагинация)"),
        limit: int = Query(
            10,
            description="Максимальное количество возвращаемых элементов(пагинация)"),
        tags: str = Query(None, description="Фильтрация по тегам"),
        completed: bool = Query(
            None, description="Фильтрация по статусу выполнения"),
        deadline_start: date = Query(
            None,
            description="Фильтрация  сортировкой по сроку начальная дата"),
        deadline_end: date = Query(
            None,
            description="Фильтрация  сортировкой по сроку конечная дата"),
        created_at_start: date = Query(
            None, description="Фильтрация по дате создания начальная дата"),
        created_at_end: date = Query(
            None, description="Фильтрация по дате создания конечная дата"),
        title: str = Query(None, description="Фильтрация по заголовкам"),
        session: AsyncSession = Depends(get_async_session)):
    """ Эндпойнт плучение списка дел с фильтром по тегам, статусу выполнения,
          сортировкой по сроку, дате создания, заголовку и пагинацией,
          фильтрацию можно делать по одному полю так и по нескольким полям """
    try:
        service = ItemService()
        task_list = await service.get_task_list(skip, limit, tags, completed,
                                                deadline_start, deadline_end,
                                                created_at_start,
                                                created_at_end,
                                                title, session)
        return task_list
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=500, detail=f"Ошибка базы данных: {e}")
