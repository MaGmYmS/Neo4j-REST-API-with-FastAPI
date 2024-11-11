# test_query.py
import pytest
from Neo4jQueries import Neo4jQueries


@pytest.fixture
def db():
    db = Neo4jQueries("bolt://localhost:7687", "neo4j", "123")
    yield db
    db.close()


def test_get_all_nodes(db):
    nodes = db.get_all_nodes()
    assert isinstance(nodes, list), "Должен вернуть список узлов"


def test_add_and_get_node_with_relationships(db):
    label = "User"
    properties = {"name": "Test User", "age": 30}
    relationships = []

    # Добавляем узел
    db.add_node_and_relationships(label, properties, relationships)

    # Проверяем добавленный узел
    nodes = db.get_all_nodes()
    assert any(node['label'] == label for node in nodes), "Узел не добавлен"

    # Проверяем получение связей узла
    node_id = nodes[0]['id']
    node_with_relationships = db.get_node_with_relationships(node_id)
    assert isinstance(node_with_relationships, list), "Должен вернуть список узлов со связями"


def test_delete_node(db):
    label = "User"
    properties = {"name": "ToDelete", "age": 40}
    relationships = []

    # Добавляем узел
    db.add_node_and_relationships(label, properties, relationships)
    nodes = db.get_all_nodes()

    # Удаляем узел
    node_id = next((node['id'] for node in nodes if node['label'] == label), None)
    db.delete_node(node_id)

    # Проверяем, что узел удален
    nodes = db.get_all_nodes()
    assert not any(node['id'] == node_id for node in nodes), "Узел не удален"
