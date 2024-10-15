from passlib.context import CryptContext
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from models import User
from fastapi import HTTPException
from models import Task, TaskStatus, User
from typing import List
from responses import TaskCreateBody, TaskUpdateBody
from email_validator import EmailNotValidError, validate_email

pwd_context = CryptContext(
    schemes=["bcrypt"], deprecated = "auto"
)

def add_user(
        session: Session,
        username: str,
        password: str,
        email: str,
) -> User | None:
    hashed_password = pwd_context.hash(password)
    db_user = User(
        username=username,
        email=email,
        hashed_password=hashed_password
    )
    session.add(db_user)
    try:
        session.commit()
        session.refresh(db_user)
    except IntegrityError:
        session.rollback()
        return None
    return db_user 

def get_user(
        session: Session, username_or_email: str
) -> User | None:
    try:
        validate_email(username_or_email)
        query_filter = User.email
    except EmailNotValidError:
        query_filter = User.username
    user = (
        session.query(User)
        .filter(query_filter == username_or_email)
        .first()
    )        
    return user  

# Função para criar uma nova tarefa
def create_task(session: Session, task: TaskCreateBody, current_user: User) -> Task:
    db_task = Task(
        titulo=task.titulo,
        descricao=task.descricao,
        user_id=current_user.id,
        status=TaskStatus.PENDING,  # Tarefa começa como pendente
    )
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task

# Função para listar as tarefas do usuário
def list_tasks(session: Session, current_user: User) -> List[Task]:
    tasks = session.query(Task).filter(Task.user_id == current_user.id).all()
    return tasks

# Função para atualizar uma tarefa
def update_task(session: Session, task_id: int, task_update: TaskUpdateBody, current_user: User) -> Task:
    db_task = session.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    
    if task_update.titulo:
        db_task.titulo = task_update.titulo
    if task_update.descricao:
        db_task.descricao = task_update.descricao
    if task_update.status:
        db_task.status = task_update.status
    
    session.commit()
    session.refresh(db_task)
    return db_task

# Função para deletar uma tarefa
def delete_task(session: Session, task_id: int, current_user: User):
    db_task = session.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    
    session.delete(db_task)
    session.commit()
    return