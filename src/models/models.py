from sqlalchemy import Boolean, Column, Enum, Integer, String, MetaData, DateTime, ForeignKey, func
from sqlalchemy.orm import declarative_base, relationship

metadata = MetaData()

Base = declarative_base(metadata=metadata)

"""Для более гибкого добавления тегов создаем таблицы могие ко многим"""


class Tag(Base):
    __tablename__ = 'tags'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=True)


class Task_list(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    deadline = Column(DateTime)
    completed = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    tags = relationship("Tag", secondary="task_tags",
                        backref="tasks", lazy='subquery')


class TaskTag(Base):
    __tablename__ = 'task_tags'
    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey('tasks.id'),
                     nullable=False, index=True)
    tag_id = Column(Integer, ForeignKey('tags.id'), nullable=False, index=True)
