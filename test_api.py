# test_api.py
import pytest
from fastapi.testclient import TestClient
from Neo4jQueriesAPI import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as client:
        yield client


def test_get_all_nodes(client):
    response = client.get("/nodes")
    assert response.status_code == 200
    assert isinstance(response.json(), list), "Должен вернуть список узлов"


def test_get_node(client):
    response = client.get("/nodes/326621197")
    assert response.status_code == 200, "Узел с ID 326621197 не существует"
    assert "node" in response.json()[0], "Ответ должен содержать узел"


def test_add_and_delete_node(client):
    node_data = {
        "label": "User",
        "properties": {"id": 664, "name": "Test User Alice", "age": 25},
        "relationships": []
    }
    headers = {"Authorization": "Bearer your_api_token"}

    # Создаем узел с ID 664
    create_response = client.post("/nodes", json=node_data, headers=headers)
    assert create_response.status_code == 200
    assert create_response.json() == {"message": "Node and relationships added successfully"}

    # Получаем список всех узлов и находим созданный узел
    get_nodes_response = client.get("/nodes")
    assert get_nodes_response.status_code == 200
    nodes = get_nodes_response.json()
    created_node = next((node for node in nodes if node["id"] == 664), None)
    assert created_node is not None, "Созданный узел не найден"

    # Удаляем созданный узел по его ID
    node_id = created_node["id"]
    delete_response = client.delete(f"/nodes/{node_id}", headers=headers)
    assert delete_response.status_code == 200
    assert delete_response.json() == {"message": "Node and relationships deleted successfully"}

    # Проверяем, что узел был удален
    get_nodes_response = client.get("/nodes")
    assert get_nodes_response.status_code == 200
    nodes = get_nodes_response.json()
    assert all(node["id"] != node_id for node in nodes), "Узел не был удален"
