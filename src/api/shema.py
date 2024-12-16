from datetime import date
from typing import List, Optional
from pydantic import BaseModel


class ResponseTask(BaseModel):
    """ Схема ответа редактирования и создания задач"""
    id: int
    title: str
    description: str
    deadline: Optional[date]
    completed: bool
    tags: List[str] = []


class Create_task(BaseModel):
    """Схема создания списка дел"""
    title: str
    description: str
    deadline: Optional[date] = None
    completed: bool = False
    tags: Optional[List[str]] = None
   


class Translation_completed_task(BaseModel):
    """ Схема первода в выполненные"""

    completed: Optional[bool]


class Update_task(BaseModel):
    """ Схема обновления списка дел"""
    # id: int
    title: Optional[str]
    description: Optional[str]
    deadline: Optional[date]
    completed: Optional[bool] = False
    tags: Optional[List[str]] = []



