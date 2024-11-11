from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

from Neo4jQueries import Neo4jQueries

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Создаем контекст lifespan для инициализации и закрытия соединения с базой данных
@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.db = Neo4jQueries("bolt://localhost:7687", "neo4j", "123")
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


@app.post("/nodes")
async def add_node(node: Node, token: str = Depends(oauth2_scheme)):
    app.state.db.add_node_and_relationships(node.label, node.properties, node.relationships)
    return {"message": "Node and relationships added successfully"}


@app.delete("/nodes/{id}")
async def delete_node(id: int, token: str = Depends(oauth2_scheme)):
    app.state.db.delete_node(id)
    return {"message": "Node and relationships deleted successfully"}
