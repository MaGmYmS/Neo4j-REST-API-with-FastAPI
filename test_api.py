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


def test_add_node(client):
    node_data = {
        "label": "User",
        "properties": {"name": "Alice", "age": 25},
        "relationships": []
    }
    headers = {"Authorization": "Bearer test-token"}

    response = client.post("/nodes", json=node_data, headers=headers)
    assert response.status_code == 200
    assert response.json() == {"message": "Node and relationships added successfully"}


def test_get_node(client):
    response = client.get("/nodes/146606274")  # Предполагаем, что узел с ID 146606274 существует
    if response.status_code == 404:
        pytest.skip("Тест пропущен, узел с ID 146606274 не существует")
    assert response.status_code == 200
    assert "node" in response.json()[0], "Ответ должен содержать узел"


def test_delete_node(client):
    headers = {"Authorization": "Bearer test-token"}
    response = client.delete("/nodes/1", headers=headers)  # Удаляем узел с ID 1
    if response.status_code == 404:
        pytest.skip("Тест пропущен, узел с ID 1 не существует")
    assert response.status_code == 200
    assert response.json() == {"message": "Node and relationships deleted successfully"}
