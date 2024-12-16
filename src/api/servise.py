from datetime import date
from fastapi import HTTPException
from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from api.shema import Create_task, ResponseTask, Translation_completed_task, \
    Update_task
from models.models import Tag, Task_list, TaskTag
from sqlalchemy.orm import selectinload


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

            # извлечение id для записи в промежуточную таблицу многие ко многим
            await session.flush()
            task_id = new_task.inserted_primary_key[0]

            # вызов функции добавление тегов
            add_tag = await ItemService.adding_tags(task, task_id, session)
            return add_tag

        except Exception as e:
            await session.rollback()
            raise HTTPException(
                status_code=500, detail=f"Ошибка базы данных: {e}")

    async def delete_item(self, task_id: int, session: AsyncSession):
        """ Удаление задачи по id"""
        try:
            # получение задачи по id
            result = await session.get(Task_list, task_id)
            if result is None:
                raise HTTPException(
                    status_code=404, detail="Задача не найдена")
            # удаление задачи
            await session.delete(result)
            await session.commit()
            return {"status": "deleted"}
        except Exception as e:
            await session.rollback()
            raise HTTPException(
                status_code=500, detail=f"Ошибка при удаление задачи: {e}")

    async def translation_into_completed(self,
                                         task: Translation_completed_task,
                                         task_id: int, session: AsyncSession):
        """ Перевод задачи в выполненные по id"""
        try:
            # Получение задачи по id
            result = await session.get(Task_list, task_id)
            if result is None:
                raise HTTPException(
                    status_code=404, detail="Задача не найдена")

            # Получение булевого значения completed и обновление задачи
            completed_true = dict(task).get("completed")
            if completed_true is None:
                raise HTTPException(
                    status_code=400, detail="Значение 'completed' не передано")
            # перевод задачи в выполненые
            result.completed = completed_true
            await session.commit()
            return result

        except Exception as e:
            await session.rollback()
            raise HTTPException(
                status_code=500, detail=f"Ошибка при обновлении задачи: {e}")

    async def update_task(self, task: Update_task, task_id: int,
                          session: AsyncSession):
        """ Редактирование задачи по id"""
        try:
            # получение задачи для редактирования
            query = select(Task_list).options(
                selectinload(Task_list.tags)).where(Task_list.id == task_id)
            result = await session.execute(query)
            tasks = result.scalars().first()
            if tasks is None:
                raise HTTPException(status_code=404, detail="Task not found")
            # Обновление поля задач
            # Исключение полей, которые не были явно установлены при 
            # создании экземпляра модели
            for key, value in task.dict(exclude_unset=True).items():

                if key == 'tags':
                    tasks.tags.clear()  # Удаление старых тегов
                    for tag_name in value:
                        tag = Tag(name=tag_name)  # Добавляются поля Tag
                        tasks.tags.append(tag)  # Добавляется новый тег
                else:
                    setattr(tasks, key, value)  # Обновляются поля Task_Tag

            await session.commit()
            return ResponseTask(
                id=tasks.id,
                title=tasks.title,
                description=tasks.description,
                deadline=tasks.deadline,
                completed=tasks.completed,
                tags=[tag.name for tag in tasks.tags]
            )

        except Exception as e:
            await session.rollback()
            raise HTTPException(
                status_code=500, detail=f"Ошибка базы данных: {e}")

    async def get_task_list(self, skip: int,
                            limit: int,
                            tags: str,
                            completed: bool,
                            deadline_start: date,
                            deadline_end: date,
                            created_at_start: date,
                            created_at_end: date,
                            title: str,

                            session: AsyncSession):
        """ Просмотр всех задач с фильтром по тегам, статусу выполнения,
          сортировкой по сроку, дате создания, заголовку и пагинацией."""
        try:
            query = select(Task_list).options(
                selectinload(Task_list.tags)).offset(
                skip).limit(limit)

            if completed is not None:
                query = query.filter(Task_list.completed == completed)

            if tags:
                query = query.filter(Task_list.tags.any(name=tags))

            if deadline_start and deadline_end:
                query = query.filter(Task_list.deadline.between(
                    deadline_start, deadline_end))

            if created_at_start and created_at_end:
                query = query.filter(Task_list.created_at.between(
                    created_at_start, created_at_end))

            if title:
                query = query.filter(Task_list.title.ilike(f"%{title}%"))

            result = await session.execute(query)
            tasks = result.scalars().all()
            return tasks
        except Exception as e:
            await session.rollback()
            raise HTTPException(
                status_code=500, detail=f"Ошибка базы данных: {e}")

    @staticmethod
    async def adding_tags(task, task_id: int, session: AsyncSession):
        """ Добавление тегов"""

        try:
            # провека есть ли записи тегов в таблице Tag
            tags_added = []
            if task.tags:
                existing_tags = await session.execute(
                    select(Tag).where(Tag.name.in_(task.tags))
                )
                existing_tag_names = {
                    tag.name: tag.id for tag in existing_tags.scalars()}

                # если есть записи тегов получаeм id, в другом случае
                # записываем в таблицу Tag и также получаем id и записываем в
                #  промежуточную таблицу TaskTag связи многие ко многим
                for tag_name in task.tags:
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
