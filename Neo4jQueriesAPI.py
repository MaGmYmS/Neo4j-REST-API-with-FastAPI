import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from Neo4jQueries import Neo4jQueries

# Чтение токена и учетных данных базы данных из переменных окружения
DB_URI = "bolt://localhost:7687"
DB_USERNAME = os.getenv("NEO4J_USERNAME")
DB_PASSWORD = os.getenv("NEO4J_PASSWORD")
API_TOKEN = os.getenv("API_TOKEN")

if not DB_USERNAME or not DB_PASSWORD or not API_TOKEN:
    raise EnvironmentError("Отсутствуют необходимые переменные окружения: NEO4J_USERNAME, NEO4J_PASSWORD, API_TOKEN")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Проверка токена авторизации
def get_current_token(token: str = Depends(oauth2_scheme)):
    if token != API_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token {token}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token


# Создаем контекст lifespan для инициализации и закрытия соединения с базой данных
@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.db = Neo4jQueries(DB_URI, DB_USERNAME, DB_PASSWORD)
    yield
    app.state.db.close()


app = FastAPI(lifespan=lifespan)


class Node(BaseModel):
    label: str
    properties: dict
    relationships: list


@app.get("/nodes")
async def get_all_nodes():
    nodes = app.state.db.get_all_nodes()
    return nodes


@app.get("/nodes/{id}")
async def get_node(id: int):
    node = app.state.db.get_node_with_relationships(id)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    return node


@app.post("/nodes", dependencies=[Depends(get_current_token)])
async def add_node(node: Node):
    app.state.db.add_node_and_relationships(node.label, node.properties, node.relationships)
    return {"message": "Node and relationships added successfully"}


@app.delete("/nodes/{id}", dependencies=[Depends(get_current_token)])
async def delete_node(id: int):
    app.state.db.delete_node(id)
    return {"message": "Node and relationships deleted successfully"}
