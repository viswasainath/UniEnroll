from neo4j import GraphDatabase, Driver
from typing import Generator
import logging
from .config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD

logger = logging.getLogger("unienroll.database")

class Neo4jManager:
    _driver: Driver | None = None

    @classmethod
    def get_driver(cls) -> Driver:
        if cls._driver is None:
            logger.info(f"Connecting to Neo4j at {NEO4J_URI} as {NEO4J_USER}")
            cls._driver = GraphDatabase.driver(
                NEO4J_URI,
                auth=(NEO4J_USER, NEO4J_PASSWORD),
                max_connection_lifetime=3600,
                max_connection_pool_size=50,
                connection_acquisition_timeout=30.0
            )
        return cls._driver

    @classmethod
    def close(cls):
        if cls._driver is not None:
            logger.info("Closing Neo4j driver connection")
            cls._driver.close()
            cls._driver = None

    @classmethod
    def check_connection(cls) -> dict:
        driver = cls.get_driver()
        with driver.session() as session:
            result = session.run("RETURN 1 AS ping").single()
            node_counts = {}
            labels_res = session.run("CALL db.labels() YIELD label RETURN label")
            for record in labels_res:
                label = record["label"]
                cnt_res = session.run(f"MATCH (n:{label}) RETURN count(n) AS c").single()
                node_counts[label] = cnt_res["c"] if cnt_res else 0
            
            rel_res = session.run("MATCH ()-[r]->() RETURN count(r) AS rel_count").single()
            rel_count = rel_res["rel_count"] if rel_res else 0

            return {
                "status": "healthy",
                "connected": result is not None and result["ping"] == 1,
                "node_counts": node_counts,
                "total_relationships": rel_count,
                "uri": NEO4J_URI,
                "user": NEO4J_USER
            }

def get_db_session() -> Generator:
    driver = Neo4jManager.get_driver()
    session = driver.session()
    try:
        yield session
    finally:
        session.close()
