from neo4j import GraphDatabase
import random
from config.settings import settings
from core.logger import get_logger

logger = get_logger(__name__)

class Neo4jSeeder:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password)
        )

    def close(self):
        self.driver.close()

    def seed(self):
        with self.driver.session() as session:
            try:
                logger.info("Starting Neo4j seed process...")

                logger.info("Creating index on Account(id)...")
                session.run("CREATE INDEX account_id_idx IF NOT EXISTS FOR (a:Account) ON (a.id)")

                logger.info("Creating Account nodes ACC001-ACC010...")
                accounts = [f"ACC{str(i).zfill(3)}" for i in range(1, 11)]
                for acc_id in accounts:
                    session.run("MERGE (a:Account {id: $acc_id})", acc_id=acc_id)

                logger.info("Creating Mule Ring ACC001-003...")
                ring_edges = [("ACC001", "ACC002"), ("ACC002", "ACC003"), ("ACC003", "ACC001")]
                for src, dst in ring_edges:
                    session.run(
                        "MATCH (a:Account {id: $src}), (b:Account {id: $dst}) MERGE (a)-[r:SENT_TO {amount: $amt}]->(b)",
                        src=src, dst=dst, amt=round(random.uniform(1000, 10000), 2)
                    )

                logger.info("Creating Star Topology ACC004 as hub...")
                hub = "ACC004"
                receivers = accounts[4:]
                for receiver in receivers:
                    session.run(
                        "MATCH (a:Account {id: $src}), (b:Account {id: $dst}) MERGE (a)-[r:SENT_TO {amount: $amt}]->(b)",
                        src=hub, dst=receiver, amt=round(random.uniform(1000, 10000), 2)
                    )

                logger.info("Neo4j seeding completed successfully.")

            except Exception as e:
                logger.error(f"Failed to seed Neo4j: {str(e)}")
                raise

if __name__ == '__main__':
    seeder = Neo4jSeeder()
    try:
        seeder.seed()
    finally:
        seeder.close()