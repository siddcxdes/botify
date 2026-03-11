"""database.py - connects to postgresql (backend package)
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from backend.config import DATABASE_URL

# create engine to connect to our database
engine = create_engine(DATABASE_URL)

# session is like a conversation with the database
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# all our models will inherit from this
Base = declarative_base()


# this gives us a database session to use in routes
# its a generator so fastapi can handle opening and closing it
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
