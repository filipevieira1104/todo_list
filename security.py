from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from models import User
from db_connection import get_session
from email_validator import validate_email, EmailNotValidError
from operations import pwd_context

# Configuração de segurança
SECRET_KEY = "q*vdy9h3uzv=y=cwcr!m*qa^izlfg%1l=!^7ci(2ey#+i--4zn'"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Autentica o usuário
def authenticate_user(
        session: Session,
        username_or_email: str,
        password: str,
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
    if not user or not pwd_context.verify(
        password, user.hashed_password
    ):
        return None
    return user

# Gera o token JWT
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=60)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Obtém o usuário a partir do token JWT
async def get_current_user(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Print o token JWT recebido
    print(f"Token recebido: {token}")
    
    try:
        # Decodifica o token JWT usando a SECRET_KEY correta
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Print do payload decodificado para verificar o conteúdo
        print(f"Payload decodificado: {payload}")
        
        # Extrai o user_id do campo 'sub' do payload
        user_id: str = payload.get("sub")
        
        if user_id is None:
            raise credentials_exception
        
        # Print para verificar o ID do usuário extraído do token
        print(f"ID do usuário no token: {user_id}")
        
    except JWTError as e:
        # Print o erro de JWT para depuração
        print(f"Erro ao decodificar o token: {e}")
        raise credentials_exception
    
    # Busca o usuário no banco de dados com base no user_id
    user = session.query(User).filter(User.id == user_id).first()
    
    # Print para verificar se o usuário foi encontrado no banco
    print(f"Usuário encontrado: {user}")
    
    if user is None:
        raise credentials_exception
    return user