

from fastapi import Depends, HTTPException
from sqlalchemy import insert, select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from api.shema import Create_task, ResponseTask
from database.database import get_async_session
from models.models import Tag, Task_list, TaskTag


class ItemService:
    async def create_item(self, task: Create_task, session: AsyncSession):
        """Создание задачи"""
        try:
            # запись в таблицу в Task_list
            new_task = await session.execute(
                insert(Task_list).values(
                    title=task.title,
                    description=task.description,
                    deadline=task.deadline,
                    completed=task.completed,
                )
            )
            # извлечение id дял записи в промежуточную таблицу
            await session.flush()
            task_id = new_task.inserted_primary_key[0]

            # провека есть ли записи тегов в таблице Tag
            tags_added = []
            if task.name:
                existing_tags = await session.execute(
                    select(Tag).where(Tag.name.in_(task.name))
                )
                existing_tag_names = {
                    tag.name: tag.id for tag in existing_tags.scalars()}

                # если есть записи тегов получаeм id, в другом случае
                # записываем в таблицу Tag и также получаем id и записываем в
                #  промежуточную таблицу TaskTag связи многие ко многим
                for tag_name in task.name:
                    if tag_name in existing_tag_names:
                        tag_id = existing_tag_names[tag_name]
                        tags_added.append(tag_name)
                    else:
                        new_tag = Tag(name=tag_name)
                        session.add(new_tag)
                        await session.flush()
                        tag_id = new_tag.id
                        tags_added.append(tag_name)
                    session.add(TaskTag(task_id=task_id, tag_id=tag_id))
                await session.commit()
            else:
                await session.commit()
            return ResponseTask(id=task_id, title=task.title,
                                description=task.description,
                                deadline=task.deadline,
                                completed=task.completed,
                                tags=tags_added)
        except Exception as e:
            await session.rollback()
            raise HTTPException(
                status_code=500, detail=f"Ошибка базы данных: {e}")
