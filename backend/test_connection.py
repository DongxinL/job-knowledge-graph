from neo4j import GraphDatabase

uri = "bolt://localhost:7687"
username = "neo4j"
password = "password"

try:
    driver = GraphDatabase.driver(uri, auth=(username, password))
    driver.verify_connectivity()
    print("✅ Neo4j连接成功！")
    
    with driver.session() as session:
        result = session.run("CALL dbms.components() YIELD versions RETURN 'Hello Neo4j' AS message, versions[0] AS version")
        record = result.single()
        print(f"消息: {record['message']}")
        print(f"Neo4j版本: {record['version']}")
    
    driver.close()
except Exception as e:
    print(f"❌ 连接失败: {e}")
