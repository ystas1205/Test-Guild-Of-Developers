
from datetime import date
from typing import List, Optional
from pydantic import BaseModel, Field

class ResponseTask(BaseModel):
    id: int
    title: str
    description: str
    deadline: Optional[date]
    completed: bool
    tags: List[str] = [] 


class Create_task(BaseModel):
    title: str
    description: str
    deadline: Optional[date] = None
    completed: bool = False
    name: Optional[List[str]] = None  


