from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dbclients.discovery.host import get_network_context
import os

# SQLAlchemy Base class
Base = declarative_base()
# Get network context for DB connection
network_context = get_network_context()

# Constants for DB connection
SERVER_IP = network_context.preferred_host
DBNAME = "siphon2"
USER = "user"
PASSWORD = os.getenv("POSTGRES_PASSWORD")
USERNAME = os.getenv("POSTGRES_USERNAME")
PORT = 5432

if any(v is None for v in [PASSWORD, USERNAME]):
    raise ValueError(
        "POSTGRES_PASSWORD and POSTGRES_USERNAME environment variables must be set"
    )

POSTGRES_URL = f"postgresql://{USERNAME}:{PASSWORD}@{SERVER_IP}:{PORT}/{DBNAME}"


engine = create_engine(
    POSTGRES_URL,
    echo=False,
)


SessionLocal = sessionmaker(bind=engine)


def get_db():
    """FastAPI dependency for routes"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
