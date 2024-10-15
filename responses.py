from typing import Annotated
from pydantic import BaseModel, EmailStr, Field
from pydantic import BaseModel
from typing import Optional
from enum import Enum

class UserCreateBody(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserCreateResponse(BaseModel):
    username: str
    email: EmailStr

class ResponseCreateUser(BaseModel):
    message: Annotated[
        str, Field(default="Usuário Criado!")
    ]
    user: UserCreateResponse     

# Definição dos possíveis status de uma tarefa
class TaskStatus(str, Enum):
    PENDING = "Pendente"
    IN_PROGRESS = "Em andamento"
    COMPLETED = "Concluído"

# Esquema para a criação de uma nova tarefa
class TaskCreateBody(BaseModel):
    titulo: str
    descricao: Optional[str] = None

# Esquema para a resposta ao listar/criar uma tarefa
class TaskResponse(BaseModel):
    id: int
    titulo: str
    descricao: Optional[str]
    status: TaskStatus

    class Config:
        orm_mode = True

# Esquema para a atualização de uma tarefa
class TaskUpdateBody(BaseModel):
    titulo: Optional[str]
    descricao: Optional[str]
    status: Optional[TaskStatus]       