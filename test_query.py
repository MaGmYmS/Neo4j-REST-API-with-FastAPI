# test_query.py
import os
import pytest
from Neo4jQueries import Neo4jQueries


@pytest.fixture
def db():
    uri = "bolt://localhost:7687"
    username = os.getenv("NEO4J_USERNAME")
    password = os.getenv("NEO4J_PASSWORD")

    # Проверяем, что переменные окружения установлены
    if not username or not password:
        raise EnvironmentError("Не найдены переменные окружения NEO4J_USERNAME и NEO4J_PASSWORD")

    db = Neo4jQueries(uri, username, password)
    yield db
    db.close()


def test_get_all_nodes(db):
    nodes = db.get_all_nodes()
    assert isinstance(nodes, list), "Должен вернуть список узлов"


def test_add_and_get_node_with_relationships(db):
    label = "User"
    properties = {"id": 665, "name": "Test User", "age": 30}
    relationships = []

    # Добавляем узел с id = 666
    db.add_node_and_relationships(label, properties, relationships)

    # Проверяем, что узел добавлен
    nodes = db.get_all_nodes()
    added_node = next((node for node in nodes if node['id'] == 665), None)
    assert added_node, "Узел с id=666 не добавлен"

    # Проверяем получение связей узла по id
    node_with_relationships = db.get_node_with_relationships(665)
    assert isinstance(node_with_relationships, list), "Должен вернуть список узлов со связями"


def test_delete_node(db):
    label = "User"
    properties = {"id": 666, "name": "To Delete", "age": 40}
    relationships = []

    # Добавляем узел с id=666
    db.add_node_and_relationships(label, properties, relationships)

    # Удаляем узел с id=666
    db.delete_node(666)

    # Проверяем, что узел удален
    nodes = db.get_all_nodes()
    assert not any(node['id'] == 666 for node in nodes), "Узел с id=666 не удален"
