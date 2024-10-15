from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status, Form, Request
from models import Base
from db_connection import get_engine, get_session
from typing import Annotated
from sqlalchemy.orm import Session
from operations import add_user
from responses import ResponseCreateUser, UserCreateResponse, UserCreateBody
from typing import List
from models import User
from security import get_current_user, authenticate_user, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from responses import TaskCreateBody, TaskResponse, TaskUpdateBody
import operations
from datetime import timedelta
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=get_engine())
    yield

app = FastAPI(
    title="Gerenciador de Tarefas", lifespan=lifespan
)  

# Servir arquivos estáticos (CSS, JS, imagens)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configurando o uso de templates com Jinja2
templates = Jinja2Templates(directory="templates")

# Rota para renderizar a página de login
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# Rota para renderizar o formulário de registro
@app.get("/register", response_class=HTMLResponse)
async def show_register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

# Rota para renderizar a página de tarefas
@app.get("/tasks", response_class=HTMLResponse)
async def show_tasks_page(request: Request):
    return templates.TemplateResponse("todo_list.html", {"request": request})

# Rota para realizar o registro de um novo usuário
@app.post(
    "/register/user",
    status_code=status.HTTP_201_CREATED, 
    response_model=ResponseCreateUser
)
def register(
    user: UserCreateBody,
    session: Session = Depends(get_session),
) -> dict[str, UserCreateResponse]:
    user = add_user(session=session, **user.model_dump())
    if not user:
        raise HTTPException(
            status.HTTP_409_CONFLICT, "Usuário e email já existe"
        )
    user_response = UserCreateResponse(
        username=user.username, email=user.email
    )
    return {
        "message": "Usuário criado com sucesso!",
        "user": user_response
    }

@app.post("/token")
def login_for_access_token(
    session: Session = Depends(get_session), 
    username: str = Form(), 
    password: str = Form()
):
    user = authenticate_user(session, username, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Rota para criar uma nova tarefa
@app.post("/tasks/", response_model=TaskResponse)
def create_task(
    task: TaskCreateBody, 
    session: Session = Depends(get_session), 
    current_user: User = Depends(get_current_user)
):
    return operations.create_task(session, task, current_user)

# Rota para listar as tarefas do usuário autenticado
@app.get("/tasks/", response_model=List[TaskResponse])
def list_tasks(
    session: Session = Depends(get_session), 
    current_user: User = Depends(get_current_user)
):
    return operations.list_tasks(session, current_user)

# Rota para atualizar uma tarefa
@app.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int, 
    task_update: TaskUpdateBody, 
    session: Session = Depends(get_session), 
    current_user: User = Depends(get_current_user)
):
    return operations.update_task(session, task_id, task_update, current_user)

# Rota para deletar uma tarefa
@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int, 
    session: Session = Depends(get_session), 
    current_user: User = Depends(get_current_user)
):
    return operations.delete_task(session, task_id, current_user)