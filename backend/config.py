import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from root directory or backend directory
root_dir = Path(__file__).resolve().parent.parent
env_path = root_dir / ".env"
load_dotenv(dotenv_path=env_path)

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "vinee1871")
BACKEND_PORT = int(os.getenv("BACKEND_PORT", "8000"))
MAX_CREDIT_CAP = 27
MIN_CREDIT_CAP = 16
