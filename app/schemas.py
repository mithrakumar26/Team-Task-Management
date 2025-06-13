from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List
from models import UserRole, TaskStatus, TaskPriority

class UserBase(BaseModel):
    username: str
    email: EmailStr
    role: UserRole = UserRole.user

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        orm_mode = True

class ProjectBase(BaseModel):
    title: str
    description: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(ProjectBase):
    title: Optional[str] = None

class Project(ProjectBase):
    id: int
    creator_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    deadline: Optional[datetime] = None
    priority: TaskPriority = TaskPriority.medium
    status: TaskStatus = TaskStatus.pending

class TaskCreate(TaskBase):
    project_id: int
    assignee_id: int

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    deadline: Optional[datetime] = None
    priority: Optional[TaskPriority] = None
    status: Optional[TaskStatus] = None
    assignee_id: Optional[int] = None

class Task(TaskBase):
    id: int
    project_id: int
    assignee_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True

class CommentBase(BaseModel):
    content: str

class CommentCreate(CommentBase):
    task_id: int

class Comment(CommentBase):
    id: int
    task_id: int
    author_id: int
    created_at: datetime
    
    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None