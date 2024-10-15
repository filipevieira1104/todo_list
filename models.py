from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey, Enum
from enum import Enum as PyEnum

# Definir a base declarativa
class Base(DeclarativeBase):
    pass

# Definindo o Enum para o status da tarefa
class TaskStatus(str, Enum):
    PENDING = "Pendente"
    IN_PROGRESS = "Em andamento"
    COMPLETED = "Concluído"

# Modelo do usuário
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String, unique=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String)

    # Relacionamento com a tabela Task
    tasks = relationship("Task", back_populates="user")

# Modelo da tarefa
class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    titulo: Mapped[str] = mapped_column(String, index=True)
    descricao: Mapped[str] = mapped_column(String)
    status: Mapped[TaskStatus] = mapped_column(String)  # Usa o TaskStatus Enum

    # ForeignKey para associar com o User
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))

    # Relacionamento com a tabela User
    user = relationship("User", back_populates="tasks")