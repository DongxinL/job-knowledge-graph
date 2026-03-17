from neo4j import GraphDatabase
import logging
import os
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_constraints(driver):
    """
    Initialize constraints and indexes for the Job Knowledge Graph.
    This ensures data integrity and query performance.
    """
    constraints = [
        # Job Constraints
        # Job ID should be unique (e.g., hash of url or generated UUID)
        "CREATE CONSTRAINT job_id_unique IF NOT EXISTS FOR (j:Job) REQUIRE j.id IS UNIQUE",
        
        # Company Constraints
        # Company name should be unique
        "CREATE CONSTRAINT company_name_unique IF NOT EXISTS FOR (c:Company) REQUIRE c.name IS UNIQUE",
        
        # Skill Constraints
        # Skill name should be unique to avoid duplicates like "Python" and "python" (handle normalization in app logic)
        "CREATE CONSTRAINT skill_name_unique IF NOT EXISTS FOR (s:Skill) REQUIRE s.name IS UNIQUE",
        
        # Location Constraints
        # Location name (e.g., "Beijing", "Haidian") should be unique
        "CREATE CONSTRAINT location_name_unique IF NOT EXISTS FOR (l:Location) REQUIRE l.name IS UNIQUE",
        
        # Benefit Constraints
        "CREATE CONSTRAINT benefit_name_unique IF NOT EXISTS FOR (b:Benefit) REQUIRE b.name IS UNIQUE",
        
        # Education Constraints
        "CREATE CONSTRAINT education_level_unique IF NOT EXISTS FOR (e:Education) REQUIRE e.level IS UNIQUE",
        
        # Category Constraints (e.g., "Backend Engineer", "Data Scientist")
        "CREATE CONSTRAINT category_name_unique IF NOT EXISTS FOR (c:Category) REQUIRE c.name IS UNIQUE",

        # KnowledgeArticle Constraints (RAG knowledge base node)
        "CREATE CONSTRAINT article_id_unique IF NOT EXISTS FOR (a:KnowledgeArticle) REQUIRE a.id IS UNIQUE"
    ]

    indexes = [
        # Fulltext search index for Job title and description
        # This allows efficient text search like "Python developer in Beijing"
        "CREATE FULLTEXT INDEX job_search_index IF NOT EXISTS FOR (n:Job) ON EACH [n.title, n.description]",

        # Fulltext search index for Skill name
        "CREATE FULLTEXT INDEX skill_search_index IF NOT EXISTS FOR (n:Skill) ON EACH [n.name]",

        # Fulltext search index for KnowledgeArticle title and content (RAG retrieval)
        "CREATE FULLTEXT INDEX article_search_index IF NOT EXISTS FOR (n:KnowledgeArticle) ON EACH [n.title, n.content]",

        # Range index on Job.created_at for time-based skill trend queries
        # e.g., "which skills grew fastest in demand over the last 6 months"
        "CREATE INDEX job_created_at_index IF NOT EXISTS FOR (j:Job) ON (j.created_at)"
    ]
    
    with driver.session() as session:
        # Apply Constraints
        logger.info("Applying constraints...")
        for constraint in constraints:
            try:
                session.run(constraint)
                logger.info(f"✅ Created/Verified constraint: {constraint}")
            except Exception as e:
                logger.error(f"❌ Failed to create constraint: {e}")
        
        # Apply Indexes
        logger.info("Applying indexes...")
        for index in indexes:
            try:
                session.run(index)
                logger.info(f"✅ Created/Verified index: {index}")
            except Exception as e:
                # Indexes might already exist or have different names, ignore if 'already exists' error
                if "already exists" in str(e):
                    logger.info(f"ℹ️ Index already exists: {index}")
                else:
                    logger.error(f"❌ Failed to create index: {e}")

def main():
    # Load environment variables
    load_dotenv()
    
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    username = os.getenv("NEO4J_USERNAME", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "password")
    
    if not uri or not username or not password:
        logger.error("❌ Missing Neo4j configuration. Please check your .env file.")
        return

    try:
        driver = GraphDatabase.driver(uri, auth=(username, password))
        driver.verify_connectivity()
        logger.info("✅ Connected to Neo4j")
        
        create_constraints(driver)
        
        driver.close()
        logger.info("🎉 Schema initialization complete.")
    except Exception as e:
        logger.error(f"❌ Error connecting to Neo4j: {e}")

if __name__ == "__main__":
    main()
