from neo4j import GraphDatabase, Transaction


class Neo4jQueries:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def get_all_nodes(self):
        query = "MATCH (n) RETURN n.id AS id, labels(n) AS label"
        with self.driver.session() as session:
            result = session.run(query)
            return [{"id": record["id"], "label": record["label"][0]} for record in result]

    def get_node_with_relationships(self, node_id):
        query = """
        MATCH (n)-[r]-(m)
        WHERE n.id = $id
        RETURN n AS node, r AS relationship, m AS target_node
        """
        with self.driver.session() as session:
            result = session.run(query, id=node_id)
            nodes = []
            for record in result:
                nodes.append({
                    "node": {
                        "id": record["node"].element_id,
                        "label": record["node"].labels,
                        "attributes": dict(record["node"]),
                    },
                    "relationship": {
                        "type": record["relationship"].type,
                        "attributes": dict(record["relationship"]),
                    },
                    "target_node": {
                        "id": record["target_node"].element_id,
                        "label": record["target_node"].labels,
                        "attributes": dict(record["target_node"]),
                    }
                })
            return nodes

    def add_node_and_relationships(self, label, properties, relationships):
        with self.driver.session() as session:
            session.execute_write(self._create_node_and_relationships, label, properties, relationships)

    @staticmethod
    def _create_node_and_relationships(tx: Transaction, label, properties, relationships):
        # Создаем узел
        create_node_query = f"CREATE (n:{label} $properties) RETURN n"
        node = tx.run(create_node_query, properties=properties).single()["n"]
        node_id = node.element_id  # Изменено на element_id

        # Создаем связи
        for relationship in relationships:
            tx.run("""
            MATCH (n), (m)
            WHERE n.id = $node_id AND m.id = $target_id
            CREATE (n)-[r:RELATIONSHIP_TYPE]->(m)
            SET r = $relationship_attributes
            """, node_id=node_id, target_id=relationship['target_id'],
                   relationship_attributes=relationship['attributes'])

    def delete_node(self, node_id):
        with self.driver.session() as session:
            session.execute_write(self._delete_node, node_id)

    @staticmethod
    def _delete_node(tx: Transaction, node_id):
        # Удаляем узел и все связанные с ним связи
        tx.run("MATCH (n) WHERE n.id = $id DETACH DELETE n", id=node_id)  # Изменено на element_id


if __name__ == "__main__":
    # Настройки подключения к базе данных
    uri = "bolt://localhost:7687"
    user = "neo4j"
    password = "123"

    # Инициализация класса
    db = Neo4jQueries(uri, user, password)

    # Проверка получения всех узлов
    print("Получение всех узлов:")
    all_nodes = db.get_all_nodes()
    print(all_nodes[5000], sep="\n")

    # Проверка получения узла по идентификатору (проверяем первый узел, если он существует)
    if all_nodes:
        first_node_id = 146606274
        print(f"\nПолучение узла с ID {first_node_id} и его связей:")
        node_with_relationships = db.get_node_with_relationships(first_node_id)
        print(node_with_relationships)
    else:
        print("Нет узлов для проверки.")

    # Проверка добавления нового узла и связей
    new_label = "User"
    new_properties = {"name": "Alice", "age": 25}
    new_relationships = [{"target_id": 326621197, "attributes": {"since": "2024"}}]
    print("\nДобавление нового узла и связей:")
    db.add_node_and_relationships(new_label, new_properties, new_relationships)
    print("Новый узел и связи добавлены.")

    # Проверка, что узел добавился
    query = """
    MATCH (n:User {name: $name})
    RETURN n AS node
    """
    with db.driver.session() as session:
        result = session.run(query, name=new_properties["name"])
        record = result.single()

        if record is not None:
            print(f"Узел успешно добавлен! Атрибуты: {dict(record['node'])}")
        else:
            print("Узел не найден.")

    # Удаление всех узлов с именем "Alice" и возрастом 25
    name_to_delete = "Alice"
    age_to_delete = 25

    # Запрос для поиска узлов, которые нужно удалить
    query = """
    MATCH (n:User {name: $name, age: $age})
    RETURN id(n) AS id
    """

    with db.driver.session() as session:
        # Получаем все ID узлов, которые нужно удалить
        result = session.run(query, name=name_to_delete, age=age_to_delete)
        node_ids_to_delete = [record["id"] for record in result]

    # Удаляем найденные узлы с помощью метода delete_node
    if node_ids_to_delete:
        print(f"\nУдаление узлов с именем '{name_to_delete}' и возрастом {age_to_delete}:")
        for node_id in node_ids_to_delete:
            db.delete_node(node_id)
        print("Узлы удалены.")
    else:
        print("Нет узлов для удаления.")

    # Закрываем соединение с базой данных
    db.close()
